# Ollama_PDF_RAG.py
# 다중 PDF 처리 지원 버전

import gradio as gr
import ollama
import os
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
# LangChain 0.3.x 버전 호환성을 위한 import
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
# Document import 호환성
try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 설정
PDFS_DIR = "PDFs"  # PDF 파일 저장 폴더
CACHE_DIR = "cache"  # 벡터 캐시 저장 폴더
EMBEDDING_MODEL = "mxbai-embed-large"
LLM_MODEL = "llama3"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DEFAULT_TOP_K = 5
DEFAULT_SCORE_THRESHOLD = 0.7
MAX_CONTEXT_LENGTH = 3000

# 프롬프트 템플릿
SYSTEM_PROMPT = """당신은 PDF 문서를 분석하는 전문 AI 어시스턴트입니다.

**역할:**
- 사용자의 질문에 대해 PDF 문서의 내용을 기반으로 정확하고 상세한 답변을 제공합니다.
- 답변은 반드시 제공된 컨텍스트에 기반해야 하며, 추측하지 않습니다.
- 여러 문서에서 정보를 찾은 경우, 각 문서의 출처를 명확히 표시합니다.
- 컨텍스트에 없는 내용은 "문서에 해당 정보가 없습니다"라고 명확히 말합니다.

**답변 형식:**
1. 핵심 답변 (간결하게)
2. 상세 설명 (필요시)
3. 관련 정보 (있는 경우)
4. 출처 문서 및 페이지 (가능한 경우)

**언어:** 한국어로 답변하며, 적절한 이모지를 사용합니다."""

USER_PROMPT_TEMPLATE = """다음은 여러 PDF 문서에서 추출한 관련 컨텍스트입니다:

{context}

**사용자 질문:** {question}

위 컨텍스트를 바탕으로 질문에 답변해주세요. 여러 문서에서 정보를 찾은 경우, 각 문서의 출처를 명시해주세요. 컨텍스트에 없는 내용은 추측하지 마세요."""


# ==================== 유틸리티 함수 ====================

def get_file_hash(file_path: str) -> str:
    """파일의 MD5 해시 계산"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"파일 해시 계산 실패: {e}")
        # 파일명과 크기로 대체 해시 생성
        stat = os.stat(file_path)
        return hashlib.md5(f"{file_path}{stat.st_size}{stat.st_mtime}".encode()).hexdigest()


def get_cache_path(file_hash: str) -> str:
    """해시 기반 캐시 경로 생성"""
    return os.path.join(CACHE_DIR, file_hash)


def is_cached(file_hash: str) -> bool:
    """캐시 존재 여부 확인"""
    cache_path = get_cache_path(file_hash)
    sqlite_path = os.path.join(cache_path, "chroma.sqlite3")
    return os.path.exists(cache_path) and os.path.exists(sqlite_path)


def load_cache_metadata(file_hash: str) -> Optional[dict]:
    """캐시 메타데이터 로드"""
    cache_path = get_cache_path(file_hash)
    metadata_path = os.path.join(cache_path, "metadata.json")
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"메타데이터 로드 실패: {e}")
    return None


def save_cache_metadata(file_hash: str, file_path: str, chunk_count: int):
    """캐시 메타데이터 저장"""
    cache_path = get_cache_path(file_hash)
    os.makedirs(cache_path, exist_ok=True)
    
    metadata = {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "file_hash": file_hash,
        "created_at": datetime.now().isoformat(),
        "chunk_count": chunk_count,
        "embedding_model": EMBEDDING_MODEL
    }
    
    metadata_path = os.path.join(cache_path, "metadata.json")
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"메타데이터 저장 실패: {e}")


def get_pdf_files() -> List[str]:
    """PDFs 폴더에서 PDF 파일 목록 가져오기"""
    if not os.path.exists(PDFS_DIR):
        os.makedirs(PDFS_DIR, exist_ok=True)
        return []
    
    pdf_files = []
    for file in os.listdir(PDFS_DIR):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(PDFS_DIR, file))
    
    return sorted(pdf_files)


# ==================== PDF 처리 함수 ====================

def load_and_vectorize_pdf(file_path: str, force_reload: bool = False) -> Optional[Chroma]:
    """
    PDF 로드 및 벡터화 (캐싱 지원)
    
    Args:
        file_path: PDF 파일 경로
        force_reload: True면 캐시 무시하고 재벡터화
    
    Returns:
        Chroma 벡터 스토어 객체 (실패시 None)
    """
    if not os.path.exists(file_path):
        logger.error(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    
    file_hash = get_file_hash(file_path)
    cache_path = get_cache_path(file_hash)
    
    # 캐시 확인
    if not force_reload and is_cached(file_hash):
        logger.info(f"✅ 캐시에서 벡터 스토어 로드: {os.path.basename(file_path)} ({file_hash[:8]}...)")
        metadata = load_cache_metadata(file_hash)
        if metadata:
            logger.info(f"   캐시 생성일: {metadata.get('created_at', '알 수 없음')}")
            logger.info(f"   청크 개수: {metadata.get('chunk_count', '?')}")
        
        try:
            embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
            vectorstore = Chroma(
                persist_directory=cache_path,
                embedding_function=embeddings
            )
            return vectorstore
        except Exception as e:
            logger.error(f"캐시 로드 실패: {e}, 재벡터화 진행...")
            force_reload = True
    
    # 새로 벡터화
    logger.info(f"🔄 새로 벡터화 중: {os.path.basename(file_path)}")
    
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
    except Exception as e:
        logger.error(f"PDF 파일을 읽을 수 없습니다: {e}")
        return None
    
    if not docs:
        logger.error("PDF에서 텍스트를 추출할 수 없습니다.")
        return None
    
    logger.info(f"   로드된 페이지 수: {len(docs)}")
    
    # 메타데이터 강화
    file_name = os.path.basename(file_path)
    for doc in docs:
        if "source" not in doc.metadata:
            doc.metadata["source"] = file_name
        doc.metadata["file_path"] = file_path
        doc.metadata["file_hash"] = file_hash
        doc.metadata["loaded_at"] = datetime.now().isoformat()
    
    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    
    logger.info(f"   생성된 청크 수: {len(splits)}")
    
    # 청크별 메타데이터 추가
    for i, split in enumerate(splits):
        split.metadata["chunk_id"] = i
        if "start_index" in split.metadata:
            split.metadata["chunk_index"] = split.metadata["start_index"]
    
    # 벡터화
    try:
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=cache_path
        )
        vectorstore.persist()
        
        # 메타데이터 저장
        save_cache_metadata(file_hash, file_path, len(splits))
        
        logger.info(f"✅ 벡터화 완료 및 캐시 저장: {cache_path}")
        return vectorstore
    except Exception as e:
        logger.error(f"벡터화 실패: {e}")
        return None


def get_retriever(vectorstore: Chroma, top_k: int = DEFAULT_TOP_K, 
                  score_threshold: float = DEFAULT_SCORE_THRESHOLD):
    """
    최적화된 리트리버 생성
    
    Args:
        vectorstore: Chroma 벡터 스토어
        top_k: 검색할 최대 문서 개수
        score_threshold: 최소 유사도 점수 (0.0-1.0)
    """
    return vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": top_k,
            "score_threshold": score_threshold
        }
    )


def search_multiple_pdfs(pdf_files: List[str], question: str, 
                         top_k: int = DEFAULT_TOP_K,
                         score_threshold: float = DEFAULT_SCORE_THRESHOLD) -> List[Document]:
    """
    여러 PDF에서 동시에 검색
    
    Args:
        pdf_files: 검색할 PDF 파일 경로 리스트
        question: 검색 질문
        top_k: 각 PDF당 검색할 문서 개수
        score_threshold: 최소 유사도 점수
    
    Returns:
        검색된 문서 리스트 (중복 제거 및 정렬)
    """
    all_docs = []
    
    for pdf_path in pdf_files:
        try:
            vectorstore = load_and_vectorize_pdf(pdf_path)
            if vectorstore is None:
                logger.warning(f"벡터 스토어 로드 실패: {pdf_path}")
                continue
            
            retriever = get_retriever(vectorstore, top_k, score_threshold)
            docs = retriever.invoke(question)
            
            # 각 문서에 PDF 소스 정보 추가
            for doc in docs:
                doc.metadata["pdf_source"] = os.path.basename(pdf_path)
                all_docs.append(doc)
            
            logger.info(f"   {os.path.basename(pdf_path)}: {len(docs)}개 문서 검색됨")
        except Exception as e:
            logger.error(f"검색 중 오류 ({pdf_path}): {e}")
            continue
    
    # 중복 제거 (내용 기반)
    seen_content = set()
    unique_docs = []
    for doc in all_docs:
        content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_docs.append(doc)
    
    # 유사도 점수로 정렬 (있는 경우)
    try:
        unique_docs.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
    except:
        pass
    
    logger.info(f"총 {len(unique_docs)}개 고유 문서 검색됨 ({len(pdf_files)}개 PDF에서)")
    return unique_docs


def format_docs(docs: List[Document]) -> str:
    """메타데이터를 포함한 문서 포맷팅"""
    if not docs:
        return ""
    
    formatted = []
    for i, doc in enumerate(docs, 1):
        pdf_source = doc.metadata.get("pdf_source", doc.metadata.get("source", "알 수 없음"))
        page = doc.metadata.get("page", doc.metadata.get("page_number", "?"))
        chunk_id = doc.metadata.get("chunk_id", i)
        score = doc.metadata.get("score", "")
        score_str = f" (유사도: {score:.3f})" if score else ""
        
        header = f"[출처 {i}: {pdf_source} - 페이지 {page} - 청크 {chunk_id}{score_str}]"
        formatted.append(f"{header}\n{doc.page_content}")
    
    return "\n\n".join(formatted)


def create_rag_prompt(question: str, context: str, max_length: int = MAX_CONTEXT_LENGTH) -> str:
    """
    RAG 프롬프트 생성 (컨텍스트 길이 제한)
    """
    # 컨텍스트 길이 제한
    if len(context) > max_length:
        context = context[:max_length] + "...\n[내용이 잘렸습니다]"
        logger.warning(f"컨텍스트가 {max_length}자를 초과하여 잘렸습니다.")
    
    return USER_PROMPT_TEMPLATE.format(
        question=question,
        context=context
    )


# ==================== RAG 체인 ====================

def rag_chain_multi(selected_pdfs: List[str], question: str, 
                    top_k: int = DEFAULT_TOP_K,
                    score_threshold: float = DEFAULT_SCORE_THRESHOLD) -> str:
    """
    다중 PDF RAG 체인 실행
    
    Args:
        selected_pdfs: 선택된 PDF 파일 경로 리스트
        question: 사용자 질문
        top_k: 검색할 문서 개수
        score_threshold: 최소 유사도 점수
    """
    start_time = datetime.now()
    
    try:
        # 입력 검증
        if not selected_pdfs:
            return "❌ PDF 파일을 선택해주세요."
        
        if not question or not question.strip():
            return "⚠️ 질문을 입력해주세요."
        
        if len(question.strip()) < 3:
            return "⚠️ 질문이 너무 짧습니다. 더 구체적으로 작성해주세요."
        
        # 여러 PDF에서 검색
        search_start = datetime.now()
        try:
            retrieved_docs = search_multiple_pdfs(selected_pdfs, question, top_k, score_threshold)
        except Exception as e:
            logger.error(f"검색 실패: {e}", exc_info=True)
            return f"🔍 문서 검색 중 오류가 발생했습니다: {str(e)}"
        
        search_time = (datetime.now() - search_start).total_seconds()
        logger.info(f"문서 검색 시간: {search_time:.2f}초")
        
        if not retrieved_docs:
            return f"❌ 선택한 {len(selected_pdfs)}개 PDF에서 관련 문서를 찾을 수 없습니다. 질문을 더 구체적으로 작성해 보거나 다른 PDF를 선택해 보세요."
        
        # 컨텍스트 포맷팅
        context = format_docs(retrieved_docs)
        logger.info(f"컨텍스트 길이: {len(context)}자 (문서: {len(retrieved_docs)}개)")
        
        # 프롬프트 생성
        prompt = create_rag_prompt(question, context)
        
        # LLM 호출
        llm_start = datetime.now()
        try:
            response = ollama.chat(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            )
            answer = response['message']['content']
        except ConnectionError:
            return "❌ Ollama 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인해주세요.\n\n터미널에서 'ollama serve' 명령을 실행해주세요."
        except Exception as e:
            logger.error(f"LLM 호출 실패: {e}", exc_info=True)
            return f"❌ 답변 생성 중 오류가 발생했습니다: {str(e)}"
        
        llm_time = (datetime.now() - llm_start).total_seconds()
        total_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"""
        ========== 성능 통계 ==========
        - 검색한 PDF 수: {len(selected_pdfs)}개
        - 검색된 문서: {len(retrieved_docs)}개
        - 문서 검색: {search_time:.2f}초
        - LLM 생성: {llm_time:.2f}초
        - 총 시간: {total_time:.2f}초
        ==============================
        """)
        
        return answer
        
    except Exception as e:
        logger.exception("예상치 못한 오류")
        return f"❌ 예상치 못한 오류가 발생했습니다: {str(e)}\n\n오류 타입: {type(e).__name__}"


def rag_chain_single(file, question: str, top_k: int = DEFAULT_TOP_K,
                     score_threshold: float = DEFAULT_SCORE_THRESHOLD) -> str:
    """
    단일 PDF RAG 체인 실행 (기존 호환성 유지)
    """
    if not file or not hasattr(file, 'name'):
        return "❌ 파일이 업로드되지 않았습니다."
    
    return rag_chain_multi([file.name], question, top_k, score_threshold)


# ==================== Gradio 인터페이스 ====================

def create_interface():
    """Gradio 인터페이스 생성"""
    
    # PDF 파일 목록 가져오기
    pdf_files = get_pdf_files()
    pdf_choices = [os.path.basename(pdf) for pdf in pdf_files]
    
    with gr.Blocks(title="PDF RAG 시스템 (다중 PDF 지원)") as iface:
        gr.Markdown("""
        # 📚 PDF 기반 질문 응답 시스템 (다중 PDF 지원)
        
        여러 PDF 파일을 선택하고 질문을 입력하면, 모든 문서를 동시에 검색하여 답변을 제공합니다.
        
        **주요 기능:**
        - ✅ 다중 PDF 동시 검색
        - ✅ 파일 해시 기반 캐싱 (빠른 재질문)
        - ✅ 각 PDF별 독립 캐시 폴더
        - ✅ 최적화된 문서 검색
        - ✅ 성능 모니터링
        """)
        
        with gr.Tabs():
            # 다중 PDF 검색 탭
            with gr.Tab("📚 다중 PDF 검색"):
                with gr.Row():
                    with gr.Column():
                        pdf_checkboxes = gr.CheckboxGroup(
                            label="📄 검색할 PDF 파일 선택",
                            choices=pdf_choices,
                            value=pdf_choices[:3] if len(pdf_choices) >= 3 else pdf_choices,
                            info="여러 PDF를 선택하여 동시에 검색할 수 있습니다."
                        )
                        
                        question_input = gr.Textbox(
                            label="❓ 질문을 입력하세요",
                            placeholder="예: 이 문서들의 주요 내용은 무엇인가요?",
                            lines=3
                        )
                        
                        with gr.Accordion("⚙️ 고급 설정", open=False):
                            top_k_slider = gr.Slider(
                                minimum=1,
                                maximum=10,
                                value=DEFAULT_TOP_K,
                                step=1,
                                label="PDF당 검색할 문서 개수 (Top K)"
                            )
                            threshold_slider = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=DEFAULT_SCORE_THRESHOLD,
                                step=0.05,
                                label="최소 유사도 점수"
                            )
                        
                        submit_btn = gr.Button("🚀 질문하기", variant="primary")
                        refresh_btn = gr.Button("🔄 PDF 목록 새로고침")
                    
                    with gr.Column():
                        output = gr.Textbox(
                            label="💬 답변",
                            lines=15,
                            interactive=False
                        )
            
            # 단일 PDF 업로드 탭 (기존 기능 유지)
            with gr.Tab("📄 단일 PDF 업로드"):
                with gr.Row():
                    with gr.Column():
                        file_input = gr.File(
                            label="📄 PDF 파일 업로드",
                            type="filepath",
                            file_types=[".pdf"]
                        )
                        
                        question_input_single = gr.Textbox(
                            label="❓ 질문을 입력하세요",
                            placeholder="예: 이 문서의 주요 내용은 무엇인가요?",
                            lines=3
                        )
                        
                        submit_btn_single = gr.Button("🚀 질문하기", variant="primary")
                    
                    with gr.Column():
                        output_single = gr.Textbox(
                            label="💬 답변",
                            lines=15,
                            interactive=False
                        )
        
        # 이벤트 핸들러
        def get_selected_pdf_paths(selected_names):
            """선택된 PDF 이름을 경로로 변환"""
            if not selected_names:
                return []
            # 현재 PDF 파일 목록 가져오기
            current_pdfs = get_pdf_files()
            current_choices = [os.path.basename(pdf) for pdf in current_pdfs]
            return [os.path.join(PDFS_DIR, name) for name in selected_names if name in current_choices]
        
        def handle_submit(names, q, k, t):
            """제출 핸들러"""
            try:
                pdf_paths = get_selected_pdf_paths(names)
                return rag_chain_multi(pdf_paths, q, k, t)
            except Exception as e:
                logger.error(f"제출 처리 중 오류: {e}", exc_info=True)
                return f"❌ 오류 발생: {str(e)}"
        
        def handle_refresh():
            """PDF 목록 새로고침"""
            try:
                new_pdfs = get_pdf_files()
                new_choices = [os.path.basename(pdf) for pdf in new_pdfs]
                return gr.CheckboxGroup.update(choices=new_choices, value=[])
            except Exception as e:
                logger.error(f"새로고침 중 오류: {e}", exc_info=True)
                return gr.CheckboxGroup.update(choices=[], value=[])
        
        submit_btn.click(
            fn=handle_submit,
            inputs=[pdf_checkboxes, question_input, top_k_slider, threshold_slider],
            outputs=output
        )
        
        refresh_btn.click(
            fn=handle_refresh,
            outputs=pdf_checkboxes
        )
        
        def handle_single_submit(file, question):
            """단일 PDF 제출 핸들러"""
            try:
                return rag_chain_single(file, question)
            except Exception as e:
                logger.error(f"단일 PDF 제출 처리 중 오류: {e}", exc_info=True)
                return f"❌ 오류 발생: {str(e)}"
        
        submit_btn_single.click(
            fn=handle_single_submit,
            inputs=[file_input, question_input_single],
            outputs=output_single
        )
        
        # 예시
        gr.Examples(
            examples=[
                ["이 문서들의 주요 내용은 무엇인가요?"],
                ["모든 문서에서 공통으로 언급된 개념을 설명해주세요."],
                ["각 문서의 결론 부분을 요약해주세요."],
            ],
            inputs=question_input
        )
    
    return iface


if __name__ == "__main__":
    # 필요한 디렉토리 생성
    os.makedirs(PDFS_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 인터페이스 실행
    try:
        iface = create_interface()
        print("✅ Gradio 인터페이스 생성 완료")
    except Exception as e:
        logger.error(f"인터페이스 생성 실패: {e}", exc_info=True)
        print(f"❌ 인터페이스 생성 중 오류 발생: {e}")
        raise
    
    # 사용 가능한 포트 찾기
    import socket
    def find_free_port(start_port=7860, max_attempts=20):
        """사용 가능한 포트 찾기"""
        for i in range(max_attempts):
            port = start_port + i
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return None
    
    # 포트 찾기
    port = find_free_port(7860)
    if port is None:
        print("⚠️ 포트 7860-7879가 모두 사용 중입니다. 8080부터 시도합니다...")
        port = find_free_port(8080, 20)
        if port is None:
            print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
            print("다른 애플리케이션을 종료하거나 환경 변수로 포트를 지정하세요:")
            print("  PowerShell: $env:GRADIO_SERVER_PORT=9000")
            raise OSError("사용 가능한 포트를 찾을 수 없습니다.")
    
    print(f"🚀 서버 시작: http://127.0.0.1:{port}")
    
    # 서버 시작
    try:
        iface.launch(
            server_name="127.0.0.1",
            server_port=port,  # 찾은 포트 사용
            share=False,
            inbrowser=False,
            show_error=True
        )
    except OSError as e:
        if "Cannot find empty port" in str(e) or "Address already in use" in str(e):
            logger.error(f"포트 충돌: {e}")
            print(f"❌ 포트 {port}가 사용 중입니다: {e}")
            print("\n해결 방법:")
            print("1. 다른 Gradio 애플리케이션이 실행 중인지 확인하고 종료하세요")
            print("2. 환경 변수로 포트 지정:")
            print("   PowerShell: $env:GRADIO_SERVER_PORT=9000")
            print("   CMD: set GRADIO_SERVER_PORT=9000")
            print("3. 또는 다른 포트 사용을 위해 코드를 수정하세요")
        else:
            logger.error(f"서버 시작 실패: {e}", exc_info=True)
            print(f"❌ 서버 시작 중 오류 발생: {e}")
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        print(f"❌ 예상치 못한 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")
        raise

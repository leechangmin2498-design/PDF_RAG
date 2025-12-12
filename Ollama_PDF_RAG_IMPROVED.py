# Ollama_PDF_RAG_IMPROVED.py
# 개선된 버전 - 주요 개선사항 적용

import gradio as gr
import ollama
import os
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 설정
VECTOR_CACHE_DIR = "chroma_pdf_cache"
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
- 컨텍스트에 없는 내용은 "문서에 해당 정보가 없습니다"라고 명확히 말합니다.

**답변 형식:**
1. 핵심 답변 (간결하게)
2. 상세 설명 (필요시)
3. 관련 정보 (있는 경우)
4. 출처 페이지 (가능한 경우)

**언어:** 한국어로 답변하며, 적절한 이모지를 사용합니다."""

USER_PROMPT_TEMPLATE = """다음은 PDF 문서에서 추출한 관련 컨텍스트입니다:

{context}

**사용자 질문:** {question}

위 컨텍스트를 바탕으로 질문에 답변해주세요. 컨텍스트에 없는 내용은 추측하지 마세요."""


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
    return os.path.join(VECTOR_CACHE_DIR, file_hash)


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


# ==================== 핵심 함수 ====================

def load_and_retrieve_pdf(file_path: str, force_reload: bool = False):
    """
    PDF 로드 및 벡터화 (캐싱 지원)
    
    Args:
        file_path: PDF 파일 경로
        force_reload: True면 캐시 무시하고 재벡터화
    
    Returns:
        Retriever 객체
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    file_hash = get_file_hash(file_path)
    cache_path = get_cache_path(file_hash)
    
    # 캐시 확인
    if not force_reload and is_cached(file_hash):
        logger.info(f"✅ 캐시에서 벡터 스토어 로드: {file_hash[:8]}...")
        metadata = load_cache_metadata(file_hash)
        if metadata:
            logger.info(f"   캐시 생성일: {metadata.get('created_at', '알 수 없음')}")
            logger.info(f"   청크 개수: {metadata.get('chunk_count', '?')}")
        
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(
            persist_directory=cache_path,
            embedding_function=embeddings
        )
        return get_optimized_retriever(vectorstore)
    
    # 새로 벡터화
    logger.info(f"🔄 새로 벡터화 중: {os.path.basename(file_path)}")
    
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
    except Exception as e:
        raise ValueError(f"PDF 파일을 읽을 수 없습니다: {e}")
    
    if not docs:
        raise ValueError("❗ PDF에서 텍스트를 추출할 수 없습니다. 다른 파일을 시도해 보세요.")
    
    logger.info(f"   로드된 페이지 수: {len(docs)}")
    
    # 메타데이터 강화
    file_name = Path(file_path).name
    for doc in docs:
        if "source" not in doc.metadata:
            doc.metadata["source"] = file_name
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
    
    return get_optimized_retriever(vectorstore)


def get_optimized_retriever(vectorstore, top_k: int = DEFAULT_TOP_K, 
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


def format_docs(docs: List) -> str:
    """메타데이터를 포함한 문서 포맷팅"""
    if not docs:
        return ""
    
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "알 수 없음")
        page = doc.metadata.get("page", doc.metadata.get("page_number", "?"))
        chunk_id = doc.metadata.get("chunk_id", i)
        
        header = f"[출처 {i}: {source} - 페이지 {page} - 청크 {chunk_id}]"
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

def rag_chain(file, question: str, top_k: int = DEFAULT_TOP_K, 
              score_threshold: float = DEFAULT_SCORE_THRESHOLD) -> str:
    """
    RAG 체인 실행
    
    Args:
        file: Gradio 파일 객체
        question: 사용자 질문
        top_k: 검색할 문서 개수
        score_threshold: 최소 유사도 점수
    """
    start_time = datetime.now()
    
    try:
        # 입력 검증
        if not file or not hasattr(file, 'name'):
            return "❌ 파일이 업로드되지 않았습니다."
        
        if not question or not question.strip():
            return "⚠️ 질문을 입력해주세요."
        
        if len(question.strip()) < 3:
            return "⚠️ 질문이 너무 짧습니다. 더 구체적으로 작성해주세요."
        
        # PDF 로드 및 벡터화
        load_start = datetime.now()
        try:
            retriever = load_and_retrieve_pdf(file.name)
        except FileNotFoundError as e:
            return f"📁 {str(e)}"
        except ValueError as e:
            return f"📄 {str(e)}"
        except Exception as e:
            logger.error(f"벡터화 실패: {e}", exc_info=True)
            return f"🔄 문서 처리 중 오류가 발생했습니다: {str(e)}"
        
        load_time = (datetime.now() - load_start).total_seconds()
        logger.info(f"문서 로드/벡터화 시간: {load_time:.2f}초")
        
        # 문서 검색
        search_start = datetime.now()
        try:
            # 동적 파라미터 조정
            question_length = len(question.split())
            if question_length < 5:
                actual_top_k = min(3, top_k)
                actual_threshold = max(0.6, score_threshold - 0.1)
            elif question_length < 15:
                actual_top_k = top_k
                actual_threshold = score_threshold
            else:
                actual_top_k = min(7, top_k + 2)
                actual_threshold = max(0.65, score_threshold - 0.05)
            
            # 리트리버 재생성 (동적 파라미터 적용)
            vectorstore = retriever.vectorstore if hasattr(retriever, 'vectorstore') else None
            if vectorstore:
                retriever = get_optimized_retriever(vectorstore, actual_top_k, actual_threshold)
            
            retrieved_docs = retriever.invoke(question)
        except Exception as e:
            logger.error(f"검색 실패: {e}", exc_info=True)
            return f"🔍 문서 검색 중 오류가 발생했습니다: {str(e)}"
        
        search_time = (datetime.now() - search_start).total_seconds()
        logger.info(f"문서 검색 시간: {search_time:.2f}초 (검색된 문서: {len(retrieved_docs)}개)")
        
        if not retrieved_docs:
            return "❌ 관련 문서를 찾을 수 없습니다. 질문을 더 구체적으로 작성해 보거나 다른 PDF를 사용해 보세요."
        
        # 컨텍스트 포맷팅
        context = format_docs(retrieved_docs)
        logger.info(f"컨텍스트 길이: {len(context)}자")
        
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
        - 문서 로드/벡터화: {load_time:.2f}초
        - 문서 검색: {search_time:.2f}초
        - LLM 생성: {llm_time:.2f}초
        - 총 시간: {total_time:.2f}초
        - 검색된 문서: {len(retrieved_docs)}개
        ==============================
        """)
        
        return answer
        
    except Exception as e:
        logger.exception("예상치 못한 오류")
        return f"❌ 예상치 못한 오류가 발생했습니다: {str(e)}\n\n오류 타입: {type(e).__name__}"


# ==================== Gradio 인터페이스 ====================

def create_interface():
    """Gradio 인터페이스 생성"""
    
    with gr.Blocks(title="PDF RAG 시스템 (개선 버전)") as iface:
        gr.Markdown("""
        # 📚 PDF 기반 질문 응답 시스템
        
        PDF 파일을 업로드하고 질문을 입력하면, 문서 내용을 기반으로 답변을 제공합니다.
        
        **주요 기능:**
        - ✅ 파일 해시 기반 캐싱 (빠른 재질문)
        - ✅ 최적화된 문서 검색
        - ✅ 구조화된 답변 형식
        - ✅ 성능 모니터링
        """)
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="📄 PDF 파일 업로드",
                    type="filepath",
                    file_types=[".pdf"]
                )
                
                question_input = gr.Textbox(
                    label="❓ 질문을 입력하세요",
                    placeholder="예: 이 문서의 주요 내용은 무엇인가요?",
                    lines=3
                )
                
                with gr.Accordion("⚙️ 고급 설정", open=False):
                    top_k_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=DEFAULT_TOP_K,
                        step=1,
                        label="검색할 문서 개수 (Top K)"
                    )
                    threshold_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=DEFAULT_SCORE_THRESHOLD,
                        step=0.05,
                        label="최소 유사도 점수"
                    )
                
                submit_btn = gr.Button("🚀 질문하기", variant="primary")
                clear_btn = gr.Button("🗑️ 초기화")
            
            with gr.Column():
                output = gr.Textbox(
                    label="💬 답변",
                    lines=15,
                    interactive=False
                )
        
        # 이벤트 핸들러
        submit_btn.click(
            fn=rag_chain,
            inputs=[file_input, question_input, top_k_slider, threshold_slider],
            outputs=output
        )
        
        clear_btn.click(
            fn=lambda: (None, "", DEFAULT_TOP_K, DEFAULT_SCORE_THRESHOLD, ""),
            outputs=[file_input, question_input, top_k_slider, threshold_slider, output]
        )
        
        # 예시
        gr.Examples(
            examples=[
                ["이 문서의 주요 내용은 무엇인가요?"],
                ["문서에서 언급된 핵심 개념을 설명해주세요."],
                ["이 문서의 결론 부분을 요약해주세요."],
            ],
            inputs=question_input
        )
    
    return iface


if __name__ == "__main__":
    # 캐시 디렉토리 생성
    os.makedirs(VECTOR_CACHE_DIR, exist_ok=True)
    
    # 인터페이스 실행
    iface = create_interface()
    iface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )


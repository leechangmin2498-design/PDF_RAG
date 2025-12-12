# import sys
# from collections import Counter
#
# n = int(sys.stdin.readline())
# cards = [int(sys.stdin.readline()) for x in range(n)]
# count = Counter(sorted(cards))
# print(count.most_common(1)[0][0])

"""
카드 숫자의 최빈값을 출력하는 프로그램입니다.
입력:
- 첫 줄: 카드 개수 N
- 다음 N개의 줄: 각 카드 숫자
출력:
- 가장 많이 나타나는 카드 숫자
"""

import sys
from collections import Counter


def main():
    n = int(sys.stdin.readline().strip())
    cards = [int(sys.stdin.readline().strip()) for _ in range(n)]
    count = Counter(sorted(cards))
    print(count.most_common(1)[0][0])


if __name__ == "__main__":
    main()

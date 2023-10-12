from typing import List


class KMPSoft:
    def __init__(self, tolerance: int) -> None:
        self.tolerance: int = tolerance

    def longest_prefix_suffix(self, pattern: List[int]) -> List[int]:
        P = len(pattern)
        pi = [0] * P
        prefix_idx = 0
        for idx in range(1, P):
            while prefix_idx >= 0 and abs(pattern[idx] - pattern[prefix_idx]) > self.tolerance:
                if prefix_idx >= 1:
                    prefix_idx = pi[prefix_idx - 1]
                else:
                    prefix_idx -= 1
            prefix_idx += 1
            pi[idx] = prefix_idx
        return pi

    def kmp(self, stream: List[int], pattern: List[int], pi: List[int]) -> List[int]:
        matches = list()
        S, P = len(stream), len(pattern)
        prefix_idx = 0
        for idx in range(S):
            while prefix_idx >= 0 and abs(stream[idx] - pattern[prefix_idx]) > self.tolerance:
                if prefix_idx >= 1:
                    prefix_idx = pi[prefix_idx - 1]
                else:
                    prefix_idx = -1
            prefix_idx += 1
            if prefix_idx == P:
                prefix_idx = pi[P - 1]
                matches.append(idx - P + 1)
        return matches

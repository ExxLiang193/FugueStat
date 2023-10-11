from typing import List, Iterable


def lsp(pattern):
    P = len(pattern)
    pi = [0] * P
    prefix_idx = 0
    for idx in range(1, P):
        while prefix_idx >= 0 and abs(pattern[idx] - pattern[prefix_idx]) > 0:
            if prefix_idx >= 1:
                prefix_idx = pi[prefix_idx - 1]
            else:
                prefix_idx -= 1
        prefix_idx += 1
        pi[idx] = prefix_idx
    return pi


def kmp(text: Iterable, pattern: Iterable) -> List[int]:
    matches = list()
    pi = lsp(pattern)
    print(pi)
    T, P = len(text), len(pattern)
    prefix_idx = 0
    for idx in range(T):
        while prefix_idx >= 0 and text[idx] != pattern[prefix_idx]:
            if prefix_idx >= 1:
                prefix_idx = pi[prefix_idx - 1]
            else:
                prefix_idx = -1
        prefix_idx += 1
        if prefix_idx == P:
            prefix_idx = pi[P - 1]
            matches.append(idx - P + 1)
    return matches


print(kmp([1, 3, 1, 2, 1, 3, 3, 1, 1, 2], [1, 3, 1, 3, 2, 1, 3]))

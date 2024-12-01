import csv
import sys
import argparse
import time
from collections import defaultdict, Counter
from itertools import combinations

def load_transactions(file_name):
    transactions = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            transactions.append(set(row))
    return transactions

def get_frequent_1_itemsets(transactions, min_support):
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1
    return {itemset: count for itemset, count in item_counts.items() if count >= min_support}

def apriori_gen(itemsets, k):
    candidates = set()
    itemsets = list(itemsets)
    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            union_set = itemsets[i] | itemsets[j]
            if len(union_set) == k and not has_infrequent_subset(union_set, itemsets):
                candidates.add(union_set)
    return candidates

def has_infrequent_subset(candidate, frequent_itemsets):
    for subset in combinations(candidate, len(candidate) - 1):
        if frozenset(subset) not in frequent_itemsets:
            return True
    return False

def filter_candidates(transactions, candidates, min_support):
    item_counts = defaultdict(int)
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                item_counts[candidate] += 1
    return {itemset: count for itemset, count in item_counts.items() if count >= min_support}

def apriori(transactions, min_support):
    frequent_itemsets = []
    current_itemsets = get_frequent_1_itemsets(transactions, min_support)
    k = 2
    while current_itemsets:
        frequent_itemsets.extend(current_itemsets.keys())
        candidates = apriori_gen(current_itemsets.keys(), k)
        current_itemsets = filter_candidates(transactions, candidates, min_support)
        k += 1
    return [set(itemset) for itemset in frequent_itemsets] 
    
def get_maximal_frequent_itemsets(frequent_itemsets):
    maximal = []
    for itemset in sorted(frequent_itemsets, key=len, reverse=True):
        if not any(set(itemset).issubset(set(max_itemset)) for max_itemset in maximal):
            maximal.append(itemset)
    return maximal

def main():
    parser = argparse.ArgumentParser(description='Apriori Algorithm Implementation')
    parser.add_argument('-i', '--input', required=True, help='Input CSV file')
    parser.add_argument('-m', '--min_support', type=int, required=True, help='Minimum support value')
    args = parser.parse_args()
    start_time = time.time()
    transactions = load_transactions(args.input)
    min_support = args.min_support
    frequent_itemsets = apriori(transactions, min_support)
    maximal_frequent_itemsets = get_maximal_frequent_itemsets(frequent_itemsets)
    maximal_frequent_itemsets.sort(key=lambda x: (len(x), x))
    print(f"Input file: {args.input}")
    print(f"Minimal support: {min_support}")
    print("{", end="")
    formatted_itemsets = [f"{{{','.join(map(str, itemset))}}}" for itemset in maximal_frequent_itemsets]
    print(",".join(formatted_itemsets), end="")
    print("}")
    print(f"\nEnd - total items: {len(maximal_frequent_itemsets)}")
    print(f"Total running time: {time.time() - start_time:.6f}")

if __name__ == '__main__':
    main()
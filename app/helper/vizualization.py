import matplotlib.pyplot as plt
import numpy as np

# Plotting character count distribution
def plot_character_distribution(character_counts):
    bins = [0, 2000, 4000, 5000, 6000, 7000, 8000, 10000, 12000, 200000]
    bin_labels = ['0-2k', '2k-4k', '4k-5k', '5k-6k', '6k-7k', '7k-8k', '8k-10k', '10k-12k', '12k-200k']
    counts, _ = np.histogram(character_counts, bins)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, counts, color='blue')
    plt.xlabel('Character Count Ranges')
    plt.ylabel('Number of Files')
    plt.title('Character Count Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/character_count_distribution.png")
    plt.close()


# Plotting word count distribution
def plot_word_distribution(word_counts):
    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2500]
    bin_labels = ['0-100', '101-200', '201-300', '301-400', '401-500', '501-600', '601-700', '701-800', '801-900', '901-1000', '1001-1200', '1201-1400', '1401-1600', '1601-1800', '1801-2000', '2001-2500']
    counts, _ = np.histogram(word_counts, bins)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, counts, color='blue')
    plt.xlabel('Word Count Ranges')
    plt.ylabel('Number of Files')
    plt.title('Word Count Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/word_count_distribution.png")
    plt.close()
"""
Huffman Compression Module
Author: Nguyễn Quốc Thắng

Description:
- Build Huffman tree
- Generate Huffman codes
- Compress data into binary form
- Decompress binary data back to original data
"""

# ==========================
# Import Libraries
# ==========================
from collections import Counter
import heapq


# ==========================
# Huffman Tree Node
# ==========================
class Node:
    """
    Node used to build the Huffman tree.
    """

    def __init__(
        self,
        char=None,
        freq=0,
        left=None,
        right=None
    ):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        """
        Compare nodes based on frequency.
        Required by heapq.
        """
        return self.freq < other.freq


# ==========================
# Huffman Tree Construction
# ==========================
def build_tree(data: bytes):
    """
    Build a Huffman tree from input data.

    Args:
        data (bytes): Input bytes.

    Returns:
        Node: Root node of the Huffman tree.
    """
    frequency_table = Counter(data)

    heap = [
        Node(char, frequency)
        for char, frequency in frequency_table.items()
    ]

    heapq.heapify(heap)

    # Handle data containing only one unique symbol
    if len(heap) == 1:
        only_node = heap[0]
        return Node(
            None,
            only_node.freq,
            only_node,
            None
        )

    while len(heap) > 1:
        left_node = heapq.heappop(heap)
        right_node = heapq.heappop(heap)

        merged_node = Node(
            None,
            left_node.freq + right_node.freq,
            left_node,
            right_node
        )

        heapq.heappush(
            heap,
            merged_node
        )

    return heap[0] if heap else None


# ==========================
# Huffman Code Generation
# ==========================
def build_codes(
    node,
    prefix="",
    codebook=None
):
    """
    Traverse the Huffman tree and generate
    binary codes.

    Args:
        node (Node): Current node.
        prefix (str): Current binary prefix.
        codebook (dict): Huffman code table.

    Returns:
        dict: Huffman codebook.
    """
    if codebook is None:
        codebook = {}

    if not node:
        return codebook

    # Leaf node
    if node.char is not None:
        codebook[node.char] = prefix or "0"

    else:
        build_codes(
            node.left,
            prefix + "0",
            codebook
        )

        build_codes(
            node.right,
            prefix + "1",
            codebook
        )

    return codebook


# ==========================
# Huffman Compression
# ==========================
def huffman_compress(data: bytes):
    """
    Compress data using Huffman coding.

    Args:
        data (bytes): Original data.

    Returns:
        tuple:
            (
                compressed_data,
                codebook,
                padding_bits
            )
    """
    if not data:
        return b"", {}, 0

    tree = build_tree(data)
    codebook = build_codes(tree)

    # Convert data to binary string
    encoded_bits = "".join(
        codebook[byte]
        for byte in data
    )

    # Add padding bits
    padding_bits = (
        8 - len(encoded_bits) % 8
    ) % 8

    encoded_bits += (
        "0" * padding_bits
    )

    # Convert bit string to bytes
    compressed_bytes = bytearray()

    for index in range(
        0,
        len(encoded_bits),
        8
    ):
        compressed_bytes.append(
            int(
                encoded_bits[
                    index:index + 8
                ],
                2
            )
        )

    return (
        bytes(compressed_bytes),
        codebook,
        padding_bits
    )


# ==========================
# Huffman Decompression
# ==========================
def huffman_decompress(
    data: bytes,
    codes: dict,
    padding_bits: int
):
    """
    Decompress Huffman encoded data.

    Args:
        data (bytes): Compressed data.
        codes (dict): Huffman codebook.
        padding_bits (int): Number of padding bits.

    Returns:
        bytes: Original data.
    """
    if not data or not codes:
        return b""

    # Reverse codebook
    reverse_codes = {
        value: key
        for key, value in codes.items()
    }

    # Convert bytes to bit string
    bit_string = "".join(
        f"{byte:08b}"
        for byte in data
    )

    if padding_bits:
        bit_string = bit_string[:-padding_bits]

    decompressed_bytes = bytearray()
    current_bits = ""

    for bit in bit_string:
        current_bits += bit

        if current_bits in reverse_codes:
            decompressed_bytes.append(
                reverse_codes[current_bits]
            )
            current_bits = ""

    return bytes(decompressed_bytes)
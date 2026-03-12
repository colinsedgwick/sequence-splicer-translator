#!/usr/bin/env python3
import argparse
import logging
import socket
import sys
from Bio.SeqIO.FastaIO import SimpleFastaParser


# -------------------------
# Logging and Command Line Inputs setup
# -------------------------
parser = argparse.ArgumentParser()
parser.add_argument(
    '-l', '--loglevel',
    type=str,
    required=False,
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    default='WARNING',
    help='set log level to DEBUG, INFO, WARNING, ERROR, or CRITICAL (default: WARNING)'
)
parser.add_argument(
    '-f', '--fastafile',
    type=str,
    required=False,
    default='',
    help='The path to the input FASTA file'
)
parser.add_argument(
    '-t', '--textbox',
    type=str,
    required=False,
    default='',
    help='The sequence input as a string (from textbox)'
)
parser.add_argument(
    '-e', '--exoncoordinates',
    type=str,
    required=True,
    help='The string of exon coordinates where exons are separated by ";" and start and end positions separated by "," (e.g. "1,12;21,39")'
)
args = parser.parse_args()

format_str = (
    f'[%(asctime)s {socket.gethostname()}] '
    '%(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
)
logging.basicConfig(level=args.loglevel, format=format_str)

# -------------------------
# Functions
# -------------------------

def fasta_processor(input_file: str) -> str:
    """
    Given input FASTA file, checks for correct number of sequences and returns the sequence of the FASTA file as a string.

    Args:
        input_file: path to input FASTA file

    Returns: 
        str: returns the DNA sequence of the FASTA file as a string
    """
    sequences = []

    logging.info(f"Reading FASTA file '{input_file}' and retrieving sequence")

    # opens FASTA file for reading, iterates through sequences and appends them to sequences list
    with open(input_file, 'r') as infile:
        for header, sequence in SimpleFastaParser(infile):
            sequences.append(sequence)

    # checks if there are 0 or greater than 1 sequences in the FASTA file, 
    # printing an error and exiting program if so
    if len(sequences) == 0:
        logging.error(f"Input FASTA file '{input_file}' contains no sequences. Exiting.")
        sys.exit(1)
    elif len(sequences) > 1:
        logging.error(f"Input FASTA file '{input_file}' contains more than one sequence. Exiting.")
        sys.exit(1)
    
    return sequences[0].upper()

def coords_string_to_tuple(exon_coordinates_string: str) -> list[tuple]:
    """
    Given input exon coordinates as a string, converts to and returns list of tuples.

    Args:
        exon_coordinates_string: string of exon coordinates where each exon is separated by ";",
                                 and start and end positions for each exon is separated by ","
                                 (e.g. "3,7;9,12;15,18")

    Returns: 
        list[tuple]: returns the exon coordinates as a list of tuples
    """

    # create list where each element is a string of a single exon's start and end position
    list_of_exon_strings = exon_coordinates_string.split(";")
    
    list_of_exon_tuples = []
    
    # iterate through each exon string and convert coordinates to tuples of integers,  then add to list of exon tuples
    for exon in list_of_exon_strings:
        exon_positions_ch = exon.split(",")
        exon_positions_int = [int(pos) for pos in exon_positions_ch]
        list_of_exon_tuples.append(tuple(exon_positions_int))

    return list_of_exon_tuples


def mature_mrna_generator(dna_sequence: str, exon_coordinates: list[tuple]) -> str:
    """
    Given input coding DNA sequence and exon coordinates, changes the T's to U's and concatenates the exons together,
    returning a string of the mature mRNA sequence.

    Args:
        dna_sequence: string of the DNA sequence to be processed
        exon_coordinates: list of tuples corresponding to exons where the first and second values in each tuple are the start and stop positions of the exon

    Returns: 
        str: returns the mature mRNA sequence as a string
    """

    logging.info(f"Generating mature mRNA transcript")

    joined_exons = ""

    # iterates through each tuple (exon) and checks for valid coordinates,
    # then adds DNA sequences corresponding to coordinates to mature_mrna string
    for exon in exon_coordinates:
        start_pos, end_pos = exon
        if not (isinstance(start_pos, int) and isinstance(end_pos, int)):
            logging.error(f"Exon coordinates must be valid integers. Exiting.")
            sys.exit(1)
        elif start_pos <= 0 or end_pos <= 0:
            logging.error(f"Exon coordinates must be integers greater than 0. Exiting.")
            sys.exit(1)
        elif start_pos > end_pos:
            logging.error(f"Exon end position must be greater than or equal to start position. Exiting.")
            sys.exit(1)
        elif start_pos > len(dna_sequence) or end_pos > len(dna_sequence):
            logging.error(f"Exon positions must be less than or equal to length of sequence. Exiting.")
            sys.exit(1)
        elif end_pos == len(dna_sequence):
            joined_exons += dna_sequence[start_pos-1:]
        else:
            joined_exons += dna_sequence[start_pos-1:end_pos]

    # replace T's with U's in the joined exons string to create mature mRNA string
    mature_mrna = joined_exons.replace("T", "U")

    return mature_mrna

def main():

    logging.info("Starting sequence processor workflow")

    if args.fastafile:
        try: 
            string_sequence = fasta_processor(args.fastafile)
        except FileNotFoundError:
            logging.error(f"Input FASTA file '{args.fastafile}' not found. Exiting.")
            sys.exit(1)
    elif not args.textbox:
        logging.error(f"Must input FASTA file path or sequence string. Exiting.")
        sys.exit(1)
    else:
        string_sequence = args.textbox
    
    exon_coordinates = coords_string_to_tuple(args.exoncoordinates)

    mature_mrna = mature_mrna_generator(string_sequence, exon_coordinates)

    print(f"Mature mRNA sequence: {mature_mrna}")

if __name__ == '__main__':
    main()


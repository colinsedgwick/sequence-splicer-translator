#!/usr/bin/env python3
import argparse
import logging
import socket
import sys
from Bio.SeqIO.FastaIO import SimpleFastaParser
from Bio.Seq import Seq


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

def cds_pos_to_tuple(cds_pos_str: str) -> tuple:
    """
    Given input coding sequence start and end positions as a string, converts to and returns tuple.

    Args:
        cds_pos_str: string of CDS coordinates where start and end positions are separated by ","
                     (e.g. "5,10")

    Returns: 
        tuple: returns the CDS start and end position as a tuple
    """

    # converts the CDS positions string to a tuple of integers of the start and end position
    cds_pos_ch = cds_pos_str.split(",")
    cds_pos_int = [int(pos) for pos in cds_pos_ch]
    cds_pos_tuple = tuple(cds_pos_int)

    return cds_pos_tuple

def mrna_translator(mature_mrna: str, cds_pos: tuple) -> str:
    """
    Given input mature mRNA string and CDS positions, generates the coding sequence 
    that is used to translate into the amino acid sequence that is returned as a string.

    Args:
        mature_mrna: string of the mature mRNA sequence to be translated
        cds_pos: tuple of the start and stop positions of the coding sequence

    Returns: 
        str: returns the amino acid sequence as a string
    """

    logging.info(f"Generating protein sequence from mRNA")

    start_pos, end_pos = cds_pos

    # checks for valid CDS coordinates and generates coding sequence
    if not (isinstance(start_pos, int) and isinstance(end_pos, int)):
        logging.error(f"CDS coordinates must be valid integers. Exiting.")
        sys.exit(1)
    elif start_pos <= 0 or end_pos <= 0:
        logging.error(f"CDS coordinates must be integers greater than 0. Exiting.")
        sys.exit(1)
    elif start_pos > end_pos:
        logging.error(f"CDS end position must be greater than or equal to start position. Exiting.")
        sys.exit(1)
    elif start_pos > len(mature_mrna) or end_pos > len(mature_mrna):
        logging.error(f"CDS positions must be less than or equal to length of sequence. Exiting.")
        sys.exit(1)
    elif end_pos == len(mature_mrna):
        coding_sequence_str = mature_mrna[start_pos-1:]
    else:
        coding_sequence_str = mature_mrna[start_pos-1:end_pos]

    # checks if generated coding sequence is multiple of 3
    if len(coding_sequence_str) % 3 != 0:
        logging.error(f"Length of coding sequence must be multiple of 3. Exiting.")
        sys.exit(1)
    
    # converts coding_sequence_str to Seq object and translates into a protein sequence, 
    # then converts protein sequence to a string 
    coding_sequence_seq = Seq(coding_sequence_str)
    protein_sequence = coding_sequence_seq.translate()
    protein_sequence_str = str(protein_sequence)

    return protein_sequence_str

def write_seq_to_fasta(fasta_file: str, header: str, sequence_str: str,) -> None:
    """
    Given output FASTA file path, header for sequence, and the sequence string, 
    writes sequence to FASTA file.

    Args:
        fasta_file: path to output FASTA file
        header: string of header for sequence
        sequence_str: sequence to be written to FASTA file

    Returns: 
        None: this function doesn't return anything; it writes a sequence to a FASTA file
    """
    logging.info(f"Writing {header} sequence to FASTA file")

    with open(fasta_file, "w") as f:
        f.write(f">{header}\n")
        f.write(f"{sequence_str}")

def main():
    
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
    parser.add_argument(
        '-c', '--cdspos',
        type=str,
        required=True,
        help='The string of CDS positions where start and end positions are separated by "," (e.g. "5,10")'
    )
    parser.add_argument(
        '-m', '--mrnafasta',
        type=str,
        required=False,
        default = '',
        help='The path to the output mRNA FASTA file'
    )
    parser.add_argument(
        '-p', '--proteinfasta',
        type=str,
        required=False,
        default = '',
        help='The path to the output protein FASTA file'
    )
    args = parser.parse_args()

    format_str = (
        f'[%(asctime)s {socket.gethostname()}] '
        '%(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
    )
    logging.basicConfig(level=args.loglevel, format=format_str)

    # -------------------------
    # Main Sequence Processing Worfklow
    # -------------------------
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

    cds_positions = cds_pos_to_tuple(args.cdspos)

    protein_sequence = mrna_translator(mature_mrna, cds_positions)

    print(f"Mature mRNA sequence: {mature_mrna}")
    if args.mrnafasta:
        write_seq_to_fasta(args.mrnafasta, "mRNA", mature_mrna)

    print(f"Protein sequence: {protein_sequence}")
    if args.proteinfasta:
        write_seq_to_fasta(args.proteinfasta, "protein", protein_sequence)


if __name__ == '__main__':
    main()
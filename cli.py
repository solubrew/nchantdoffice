#!/usr/bin/env python3
"""CLI for nchantdoffice."""
import argparse


def main():
    parser = argparse.ArgumentParser(description="nchantdoffice")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    print("nchantdoffice CLI")


if __name__ == "__main__":
    main()

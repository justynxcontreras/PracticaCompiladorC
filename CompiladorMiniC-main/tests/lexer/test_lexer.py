"""Pruebas del analizador léxico de Mini C segun la especificacion."""

import pytest
from minic.diagnostics.diagnostic_code import LEX001
from minic.lexer.lexer import Lexer
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_section_7_valid_source() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    formatted = [format_token(t) for t in tokens]
    expected = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted == expected

    # Verificar literales enteros
    assert tokens[2].literal == 12
    assert tokens[8].literal == 5
    assert tokens[0].literal is None


def test_section_7_source_with_errors() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    formatted_tokens = [format_token(t) for t in tokens]
    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert formatted_tokens == expected_tokens

    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diagnostics


def test_keywords_vs_identifiers() -> None:
    source = "int while int2 whilex _int int_ while1"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []
    token_types = [t.type for t in tokens]
    assert token_types == [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]


def test_all_single_and_double_operators() -> None:
    source = "== != = + - ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []
    token_types = [t.type for t in tokens]
    assert token_types == [
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_position_tracking_tabs_and_carriage_return() -> None:
    # \t cuenta como 1 columna
    # \r cuenta como 1 columna y no abre linea
    # \n abre linea y reinicia columna en 1
    source = "\tint\r\nx"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []
    assert len(tokens) == 3
    # \t esta en col 1, "int" empieza en col 2
    assert tokens[0].type == TokenType.KW_INT
    assert tokens[0].line == 1
    assert tokens[0].column == 2

    # despues de \r (col 5) y \n, la linea 2 empieza en col 1 para 'x'
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].line == 2
    assert tokens[1].column == 1

    # EOF esta en linea 2 col 2
    assert tokens[2].type == TokenType.EOF
    assert tokens[2].line == 2
    assert tokens[2].column == 2


def test_integer_literal_values() -> None:
    source = "007 0 42 12345678901234567890"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []
    assert tokens[0].literal == 7
    assert tokens[1].literal == 0
    assert tokens[2].literal == 42
    assert tokens[3].literal == 12345678901234567890


def test_empty_source_produces_single_eof() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].lexeme == ""
    assert tokens[0].literal is None
    assert tokens[0].line == 1
    assert tokens[0].column == 1

from pygls.server import LanguageServer
from pygls.lsp.methods import (
    COMPLETION,
    HOVER,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN
)
from pygls.lsp.types import (
    CompletionItem,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    Hover,
    HoverParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentPositionParams
)

server = LanguageServer()

# Mots-clés et fonctions du langage ADA
KEYWORDS = [
    'if', 'else', 'loop', 'define', 'make', 'out', 'in',
    'int', 'string', 'bool', 'double', 'float', 'void'
]

FUNCTIONS = [
    'write', 'read', 'convert', 'exists',
    'create_file', 'write_file', 'read_file', 'delete_file'
]

@server.feature(COMPLETION)
def completions(params: CompletionParams):
    items = []
    
    # Ajouter les mots-clés
    for keyword in KEYWORDS:
        items.append(CompletionItem(
            label=keyword,
            kind=14,  # Keyword
            detail="Keyword",
            documentation=f"ADA keyword: {keyword}"
        ))
    
    # Ajouter les fonctions
    for func in FUNCTIONS:
        items.append(CompletionItem(
            label=func,
            kind=3,  # Function
            detail="Function",
            documentation=f"ADA built-in function: {func}"
        ))
    
    return CompletionList(is_incomplete=False, items=items)

@server.feature(HOVER)
def hover(params: HoverParams):
    position = params.position
    document = server.workspace.get_document(params.text_document.uri)
    word = get_word_at_position(document, position)
    
    if word in KEYWORDS:
        return Hover(MarkupContent(
            kind=MarkupKind.Markdown,
            value=f"**{word}** - ADA keyword"
        ))
    elif word in FUNCTIONS:
        return Hover(MarkupContent(
            kind=MarkupKind.Markdown,
            value=f"**{word}** - Built-in ADA function"
        ))
    
    return None

def get_word_at_position(document, position):
    line = document.lines[position.line]
    start = position.character
    end = position.character
    
    # Trouver le début du mot
    while start > 0 and line[start-1].isalnum():
        start -= 1
    
    # Trouver la fin du mot
    while end < len(line) and line[end].isalnum():
        end += 1
    
    return line[start:end]

if __name__ == '__main__':
    server.start_io()
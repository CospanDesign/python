# syntax.py

import sys

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}


class VerilogHighlighter (QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'always', 'and', 'assign', 'automatic', 'buf', 'bufif0',
        'bufif1', 'cell', 'cmos', 'config', 'deassign', 'defparam',
        'design', 'disable', 'edge', 'endconfig', 'endfunction',
        'endgenerate', 'endmodule', 'endprimitive', 'endspecify',
        'endtable', 'endtask', 'event', 'force', 'function',
        'generate', 'genvar', 'highz0', 'highz1', 'ifnone', 'incdir',
        'include', 'initial', 'inout', 'input', 'instance', 'integer',
        'large', 'liblist', 'library', 'localparam', 'macromodule',
        'medium', 'module', 'nand', 'negedge', 'nmos', 'nor',
        'noshowcancelled', 'not', 'notif0', 'notif1', 'or', 'output',
        'parameter',  'pmos', 'posedge', 'primitive', 'pull0',
        'pull1',  'pulldown', 'pullup', 'pulsestyle_onevent',
        'pulsestyle_ondetect', 'rcmos', 'real', 'realtime',
        'reg', 'release', 'rnmos',  'rpmos', 'rtran', 'rtranif0',
        'rtranif1',  'scalared', 'showcancelled', 'signed',
        'small',  'specify', 'specparam', 'strong0', 'strong1',
        'supply0', 'supply1', 'table', 'task', 'time', 'tran',
        'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand',
        'trior', 'trireg', 'unsigned', 'use', 'vectored',
        'wait', 'wand', 'weak0', 'weak1', 'wire', 'wor',
        'xnor', 'xor'
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        #self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.multi_cmnt = (QRegExp("\/\*"), QRegExp("\*\/"), 1, STYLES['comment'])
        #self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in VerilogHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in VerilogHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in VerilogHighlighter.braces]

        # All other rules
        rules += [
            #Comments for
            #(r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            #(r'\/\*[^\\]*(\\.[^\\]*)\*\/', 0, STYLES["comment"]),
            (r'\/\*[^\\]*(\\.[^\\]*)\*\/', 0, STYLES["string"]),
            #(r"\/\**(\\.[^\*\/]*)*", 0, STYLES['string']),

            ##Double-quoted string, possibly containing escape sequences
            #(r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            ## Single-quoted string, possibly containing escape sequences
            #(r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            #(r"\/\**(\\.[^'\\]*)\*\/", 0, STYLES['comment']),

            # 'def' followed by an identifier
            #(r'\balways\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            #(r'\binitial\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'\/\/[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.multi_cmnt)


    def match_multiline(self, text, delimiter_start, delimiter_end, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter_start.indexIn(text)
            # Move past this match
            add = delimiter_start.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter_end.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter_end.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter_start.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

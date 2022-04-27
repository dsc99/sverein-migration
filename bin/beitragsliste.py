#-----------  standard imports
from os.path import join as j, basename, dirname, exists as fexists
basedir = __file__.split("/bin")[0]


from html.parser import HTMLParser

class ConvertTableToCSVParser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)

        self.csv_lines = []
        self.csv_line_values = []


    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
        if tag == "tr":
            self.csv_line_values = list()

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)
        if tag == "tr":
            self.csv_lines.append( ";".join( self.csv_line_values ) )

    def handle_data(self, data):
        print("Encountered some data  :", data)
        self.csv_line_values.append( data.strip() )

with open( j(basedir, 'beitraege.html'), "r" ) as f:
    html_text = f.read()

p = ConvertTableToCSVParser()
p.feed( html_text )
print( "\n".join(p.csv_lines) )

with open( j(basedir, 'var', 'beitrage.csv'), "w") as f:
    for l in p.csv_lines:
        f.write( l+'\n' )

pass
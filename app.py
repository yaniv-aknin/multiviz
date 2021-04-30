#!/usr/bin/env python
import subprocess
from flask import Flask, request
app = Flask(__name__)

class OptionGraph:
    def __init__(self):
        self.header = []
        self.footer = []
        self.sections = {}
        self.current = self.header
    def parse(self, filename):
        def parse_label(line):
            return line.strip().split()[1]
        current = self.header
        with open(filename) as handle:
            for line in handle:
                if '#*/' in line:
                    assert current is not self.header, 'stop before first section'
                    assert current is not self.footer, 'footer has no stop'
                    current = self.footer
                    continue
                if '/*#' in line:
                    assert current is self.header or current is self.footer, 'nested section'
                    label = parse_label(line)
                    current = self.sections[label] = []
                    continue
                current.append(line)
        return self
    def emit(self, query=()):
        result = []
        result.extend(self.header)
        for label, section in self.sections.items():
            if label in query:
                result.extend(section)
        result.extend(self.footer)
        return "".join(result)
    def list(self):
        return self.sections
graph = OptionGraph().parse('graph.dot')

@app.route('/')
def index():
    with open('index.html') as handle:
        return handle.read()

@app.route('/sections')
def sections():
    return {'sections': [{'section': section} for section in graph.list()]}

@app.route('/render')
def render():
    query = request.args.getlist('sections')
    dot = graph.emit(query).encode()
    result = subprocess.run('dot -Tsvg', input=dot, capture_output=True, shell=True).stdout
    return result, 200, {'Content-Type': 'image/svg+xml'}
    
if __name__ == '__main__':
    app.run(debug=True)

class ASTFeatures:
    def __init__(self, filepath=''):
        self.filepath = filepath

        self.count_of_nodes = 0
        self.head_nodes = []
        self.operators = {}
        self.keywords = {}
        self.literals = {}

        # unique nodes
        self.unodes = {}
        self.from_num = {}
        self.count_unodes = 0

        self.structure = []
        self.tokens = []

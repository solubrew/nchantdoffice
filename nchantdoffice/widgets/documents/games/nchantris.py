# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name:
    description: >
    version: 0.0.0.0.0.0
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.widgets.widgets import NchantdWidget
from nchantdoffice.widgets.boards import NchantdGameBoard

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "nchantris.yaml")


class NchantrisGameBoard(NchantdGameBoard):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantrisGameBoard")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantrisPiece(NchantdWidget):
    """"""

    pieces = {
        "blank": ((0, 0), (0, 0), (0, 0), (0, 0)),
        "zshape": ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        "sshape": ((0, -1), (0, 0), (1, 0), (1, 1)),
        "line": ((0, -1), (0, 0), (0, 1), (0, 2)),
        "tshape": ((-1, 0), (0, 0), (1, 0), (0, 1)),
        "square": ((0, 0), (1, 0), (0, 1), (1, 1)),
        "Lshape": ((-1, -1), (0, -1), (0, 0), (0, 1)),
        "mlshape": ((1, -1), (0, -1), (0, 0), (0, 1)),
    }

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)
        self.coords = [[0, 0] for _ in range(4)]
        self._piece_shape = Piece.NoShape
        self.set_shape(Piece.NoShape)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def shape(self):
        return self._piece_shape

    def set_shape(self, shape):
        table = TetrixPiece.coords_table[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self._piece_shape = shape

    def set_random_shape(self):
        self.set_shape(random.randint(1, 7))

    def x(self, index):
        return self.coords[index][0]

    def y(self, index):
        return self.coords[index][1]

    def set_x(self, index, x):
        self.coords[index][0] = x

    def set_y(self, index, y):
        self.coords[index][1] = y

    def min_x(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def max_x(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def min_y(self):
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def max_y(self):
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotated_left(self):
        if self._piece_shape == Piece.SquareShape:
            return self

        result = TetrixPiece()
        result._piece_shape = self._piece_shape
        for i in range(4):
            result.set_x(i, self.y(i))
            result.set_y(i, -self.x(i))

        return result

    def rotated_right(self):
        if self._piece_shape == Piece.SquareShape:
            return self

        result = TetrixPiece()
        result._piece_shape = self._piece_shape
        for i in range(4):
            result.set_x(i, -self.y(i))
            result.set_y(i, self.x(i))

        return result


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||

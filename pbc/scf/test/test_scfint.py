import unittest
import numpy
import numpy as np
from pyscf.pbc.scf import scfint
from pyscf.pbc import gto as pbcgto
import pyscf.pbc.dft as pdft


def make_cell1(L, n, nimgs=None):
    cell = pbcgto.Cell()
    cell.verbose = 0
    cell.unit = 'B'
    cell.h = ((L,0,0),(0,L,0),(0,0,L))
    cell.gs = [n,n,n]

    cell.atom = [['He', (L/2.,L/2.,L/2.)], ]
    cell.basis = { 'He': [[0, (0.8, 1.0)],
                         [0, (1.0, 1.0)],
                         [0, (1.2, 1.0)]] }
    cell.pseudo = None
    cell.nimgs = nimgs
    cell.build(False, False)
    return cell

def make_cell2(L, n, nimgs=None):
    cell = pbcgto.Cell()
    cell.build(False, False,
               unit = 'B',
               verbose = 0,
               h = ((L,0,0),(0,L,0),(0,0,L)),
               gs = [n,n,n],
               atom = [['He', (L/2.-.5,L/2.,L/2.-.5)],
                       ['He', (L/2.   ,L/2.,L/2.+.5)]],
               basis = { 'He': [[0, (0.8, 1.0)],
                                [0, (1.0, 1.0)],
                                [0, (1.2, 1.0)]] })
    return cell

def finger(mat):
    w = numpy.cos(numpy.arange(mat.size))
    return numpy.dot(mat.ravel(), w)

def get_ovlp(cell, kpt=np.zeros(3)):
    '''Get the overlap AO matrix.
    '''
    coords = pdft.gen_grid.gen_uniform_grids(cell)
    aoR = pdft.numint.eval_ao(cell, coords, kpt)
    ngs = len(aoR)
    s = (cell.vol/ngs) * np.dot(aoR.T.conj(), aoR)
    return s

def get_t(cell, kpt=np.zeros(3)):
    '''Get the kinetic energy AO matrix.

    Note: Evaluated in real space using orbital gradients, for improved accuracy.
    '''
    coords = pdft.gen_grid.gen_uniform_grids(cell)
    aoR = pdft.numint.eval_ao(cell, coords, kpt, deriv=1)
    ngs = aoR.shape[1]  # because we requested deriv=1, aoR.shape[0] = 4

    t = 0.5*(np.dot(aoR[1].T.conj(), aoR[1]) +
             np.dot(aoR[2].T.conj(), aoR[2]) +
             np.dot(aoR[3].T.conj(), aoR[3]))
    t *= (cell.vol/ngs)
    return t


class KnowValues(unittest.TestCase):
    def test_olvp(self):
        cell = make_cell1(4, 20, [2,2,2])
        s0 = get_ovlp(cell)
        s1 = scfint.get_ovlp(cell)
        self.assertAlmostEqual(numpy.linalg.norm(s0-s1), 0, 8)
        self.assertAlmostEqual(finger(s1), 1.3229918679678208, 10)

    def test_t(self):
        cell = make_cell1(4, 20, [2,2,2])
        t0 = get_t(cell)
        t1 = scfint.get_t(cell)
        self.assertAlmostEqual(numpy.linalg.norm(t0-t1), 0, 8)


if __name__ == '__main__':
    print("Full Tests for pbc.scf.hf.scfint")
    unittest.main()


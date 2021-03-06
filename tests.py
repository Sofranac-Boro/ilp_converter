import unittest
from lib.ilp_converter.StandardFormConverter import StandardFormConverter
from lib.ilp_converter.readerInterface import FileReaderInterface, get_reader
from lib.ilp_converter.problemInterface import ProblemInterface, get_problem
from mip import Model, INF
from utils import EPSEQ
import numpy as np

from typing import List, Union


def list_equal(list1: Union[List, np.ndarray], list2: Union[List, np.ndarray]) -> bool:
    for idx in range(len(list1)):
        if not EPSEQ(list1[idx], list2[idx]):
            return False
    return True


class MyTestCase(unittest.TestCase):
    def test_LiExample_end_to_end(self):
        n_cons = 4
        n_vars = 4
        nnz = 10
        m = Model()

        x1 = m.add_var("x1", 0, INF, -3)
        x2 = m.add_var("x2", 0, INF, -5)
        x3 = m.add_var("x3", 0, INF, 1)
        x4 = m.add_var("x4", 0, INF, 1)

        m += x1 +  x2 + x3 + x4 <= 40
        m +=5*x1 + x2           <= 12
        m +=            x3 + x4 >= 5
        m +=            x3 + 5*x4 <= 50

        reader: FileReaderInterface = get_reader("", model=m)

        coeffs, row_ptrs, col_indices = reader.get_cons_matrix()
        lbs, ubs = reader.get_var_bounds()

        prb: ProblemInterface = get_problem(n_cons, n_vars, coeffs, col_indices, row_ptrs, lbs, ubs, reader.get_senses(), reader.get_rhss(), reader.get_costs())

        converter = StandardFormConverter(prb)
        converter.to_standard_form()

        vals_sol =         [1, 5, 1, 1, 1, 1, 1, 1, 1, 5, 1, 1, -1, 1]
        row_indices_sol =  [0, 1, 0, 1, 0, 2, 3, 0, 2, 3, 0, 1, 2, 3]
        col_ptrs_sol    =  [0, 2, 4, 7, 10, 11, 12, 13, 14]
        ncons_sol = 4
        nvars_sol = 8
        nnz_sol = 14
        b_sol = [40, 12, 5, 50]
        costs_sol = [-3,-5,1,1, 0, 0, 0, 0]
        slack_basis_sol = [4,5,6,7]

        vals, row_indices, col_ptrs = prb.to_csc()

        self.assertTrue(list_equal(vals_sol, vals))
        self.assertTrue(list_equal(row_indices_sol, row_indices))
        self.assertTrue(list_equal(col_ptrs_sol, col_ptrs))
        self.assertTrue(prb.ncons == ncons_sol)
        self.assertTrue(prb.nvars == nvars_sol)
        self.assertTrue(col_ptrs[prb.nvars] == nnz_sol)
        self.assertTrue(list_equal(prb.costs, costs_sol))
        self.assertTrue(list_equal(converter.slack_basis,slack_basis_sol))
        self.assertTrue(list_equal(prb.b, b_sol))

    def test_BertsimasExample3_5_end_to_end(self):
        n_cons = 3
        n_vars = 3
        nnz = 9
        m = Model()

        x1 = m.add_var("x1", 0, INF, -10)
        x2 = m.add_var("x2", 0, INF, -12)
        x3 = m.add_var("x3", 0, INF, -12)

        m += 1*x1 + 2*x2 + 2*x3 <= 20
        m += 2*x1 + 1*x2 + 2*x3 <= 20
        m += 2*x1 + 2*x2 + 1*x3 <= 20

        reader: FileReaderInterface = get_reader("", model=m)

        coeffs, row_ptrs, col_indices = reader.get_cons_matrix()
        lbs, ubs = reader.get_var_bounds()

        prb: ProblemInterface = get_problem(n_cons, n_vars, coeffs, col_indices, row_ptrs, lbs, ubs, reader.get_senses(), reader.get_rhss(), reader.get_costs())

        converter = StandardFormConverter(prb)
        converter.to_standard_form()

        # testing

        vals_sol =         [1,2,2,2,1,2,2,2,1,1,1,1]
        row_indices_sol =  [0,1,2,0,1,2,0,1,2,0,1,2]
        col_ptrs_sol    =  [0,3,6,9,10,11,12]
        ncons_sol = 3
        nvars_sol = 6
        nnz_sol = 12
        b_sol = [20, 20, 20]
        costs_sol = [-10, -12, -12, 0,0,0]
        slack_basis_sol = [3,4,5]

        vals, row_indices, col_ptrs = prb.to_csc()

        self.assertTrue(list_equal(vals_sol, vals))
        self.assertTrue(list_equal(row_indices_sol, row_indices))
        self.assertTrue(list_equal(col_ptrs_sol, col_ptrs))
        self.assertTrue(prb.ncons == ncons_sol)
        self.assertTrue(prb.nvars == nvars_sol)
        self.assertTrue(col_ptrs[prb.nvars] == nnz_sol)
        self.assertTrue(list_equal(prb.costs, costs_sol))
        self.assertTrue(list_equal(converter.slack_basis,slack_basis_sol))
        self.assertTrue(list_equal(prb.b, b_sol))


if __name__ == '__main__':
    unittest.main()

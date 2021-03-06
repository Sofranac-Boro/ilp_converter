from typing import Dict
from problemInterface import ProblemInterface, Sense
from utils import INF


class StandardFormConverter:
    def __init__(self, prb: ProblemInterface) -> None:
        self.prb = prb
        # when a var x is replaced by x+ - x-, this dict holds the index map linking x to x- and x+
        # x+ takes on the index of x (key), and x- is assigned a new index (value)
        self.var_dict: Dict[int, int] = {}

        #keep track of the slack basis. This is useful for the initialization of LP algorithms
        self.slack_basis = []

        self.bounds_done = False
        self.senses_done = False
        self.equality_cons_replaced = False

    def replace_equality_constraints(self):
        for cons in range(self.prb.ncons):
            if self.prb.get_sense(cons) == Sense.EQ:
                new_cons_idx = self.prb.copy_cons(cons)
                # now set old cons as <= and new as >=
                self.prb.set_sense(cons, Sense.LE)
                self.prb.set_sense(new_cons_idx, Sense.GE)
        self.equality_cons_replaced = True

    def handle_bounds(self):
        for var in range(self.prb.nvars):
            # all bounds should be transformed to [0, INF]
            # lower bounds
            if not self.prb.is_lb_zero(var):
                self.split_var_in_two_non_negative_vars(var)
                if not self.prb.is_lb_inf(var):
                    # build new cons
                    cons = self.prb.add_cons(Sense.GE, self.prb.get_lb(var))
                    self.prb.set_coeff(cons, var, 1.0)

            # upper bounds
            if not self.prb.is_ub_inf(var):
                self.split_var_in_two_non_negative_vars(var)
                # build new cons
                cons = self.prb.add_cons(Sense.LE, self.prb.get_ub(var))
                self.prb.set_coeff(cons, var, 1.0)
        self.bounds_done = True

    def split_var_in_two_non_negative_vars(self, var: int):
        # we reuse the index var - this becomes the var+ and we add a new index (column) for var-
        # this is stored in the var_dict variable

        #if the variable is already split, do nothing
        if var not in self.var_dict.keys():
            self.var_dict[var] = self.prb.add_column()

    def replace_variables(self):
        assert self.bounds_done

        for cons in range(self.prb.ncons):
            for var in range(self.prb.nvars):
                if var in self.var_dict.keys():
                    # var takes var+ and self.var_dict[var] takes value var-. var+ already has the correct coeff,
                    # we just have to update the bounds to [0, INF]
                    self.prb.set_lb(var, 0.0)
                    self.prb.set_ub(var, INF)
                    coeff = self.prb.get_coeff(cons, var)
                    self.prb.set_coeff(cons, self.var_dict[var], -coeff)

        for var in range(self.prb.nvars):
            if var in self.var_dict.keys():
                cost = self.prb.get_cost(var)
                self.prb.set_cost(self.var_dict[var], - cost)

    def handle_sense(self):
        assert self.bounds_done
        assert self.equality_cons_replaced

        self.slack_basis_size = self.prb.ncons
        for cons in range(self.prb.ncons):
            slack_var_idx = self.prb.add_column()
            self.slack_basis.append(slack_var_idx)

            assert self.prb.get_sense(cons) != Sense.EQ

            if self.prb.get_sense(cons) == Sense.LE:
                self.prb.set_coeff(cons, slack_var_idx, 1.0)
                self.prb.set_sense(cons, Sense.EQ)

            elif self.prb.get_sense(cons) == Sense.GE:
                self.prb.set_coeff(cons, slack_var_idx, -1.0)
                self.prb.set_sense(cons, Sense.EQ)
            else:
                raise Exception("Unknown sense: ", self.prb.get_sense(cons))

        assert len(self.slack_basis) == self.prb.ncons

    def to_standard_form(self, check_validity: bool = False):
        self.replace_equality_constraints()
        self.handle_bounds()
        self.replace_variables()
        self.handle_sense()
        if check_validity:
            self.prb.check_problem_validity(self.slack_basis)











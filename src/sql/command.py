from sqlalchemy.engine import Engine

from sql import parse
from sql.store import store
from sql.connection import Connection


class SQLCommand:
    """
    Encapsulates the parsing logic (arguments, SQL code, connection string, etc.)

    """

    def __init__(self, magic, user_ns, line, cell) -> None:
        _line_set_to_cell = False
        try:
            self.args = parse.magic_args(magic.execute, line)
            # check if any argument was given
            _any_arg_given = any(value for value in list(
                self.args.__dict__.values())[1:])

            if not cell and not _any_arg_given:
                cell = line
                line = ""
                _line_set_to_cell = True
        except Exception as e:
            # Failed to parse the line but
            # the query  might work in a cell
            cell = line
            line = ""

        # Parse variables (words wrapped in {}) for %%sql magic
        # (for %sql this is done automatically)
        cell = magic.shell.var_expand(cell)

        self.args = parse.magic_args(magic.execute, line)

        # self.args.line (everything that appears after %sql/%%sql in the first line)
        # is splited in tokens (delimited by spaces), this checks if we have one arg
        one_arg = len(self.args.line) == 1

        if (
            one_arg
            and self.args.line[0] in user_ns
            and isinstance(user_ns[self.args.line[0]], Engine)
        ):
            line_for_command = []
            add_conn = True
        else:
            line_for_command = self.args.line
            add_conn = False

        if one_arg and self.args.line[0] in Connection.connections:
            line_for_command = []
            add_alias = True
        else:
            add_alias = False

        if _line_set_to_cell:
            self.command_text = " ".join(line_for_command) + cell + "\n"
        else:
            self.command_text = " ".join(line_for_command) + "\n" + cell

        if self.args.file:
            with open(self.args.file, "r") as infile:
                self.command_text = infile.read() + "\n" + self.command_text

        self.parsed = parse.parse(self.command_text, magic)

        self.parsed["sql_original"] = self.parsed["sql"]

        if add_conn:
            self.parsed["connection"] = user_ns[self.args.line[0]]

        if add_alias:
            self.parsed["connection"] = self.args.line[0]

        if self.args.with_:
            final = store.render(self.parsed["sql"], with_=self.args.with_)
            self.parsed["sql"] = str(final)

    @property
    def sql(self):
        """
        Returns the SQL query to execute, without any other options or arguments
        """
        return self.parsed["sql"]

    @property
    def sql_original(self):
        """
        Returns the raw SQL query. Might be different from `sql` if using --with
        """
        return self.parsed["sql_original"]

    @property
    def connection(self):
        """Returns the connection string"""
        return self.parsed["connection"]

    @property
    def result_var(self):
        """Returns the result_var"""
        return self.parsed["result_var"]

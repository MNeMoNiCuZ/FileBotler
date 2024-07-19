import ast

def replace_delete_with_trash(code):
    return code.replace('os.remove(', 'send2trash(').replace('os.rmdir(', 'send2trash(')

def add_print_statements(code):
    class PrintAdder(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name == 'preview_changes':
                new_body = []
                for stmt in node.body:
                    new_body.append(stmt)
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        func = stmt.value.func
                        if isinstance(func, ast.Attribute) and func.attr == 'append':
                            args = stmt.value.args
                            if len(args) >= 2:
                                print_stmt = ast.Expr(
                                    value=ast.Call(
                                        func=ast.Name(id='print', ctx=ast.Load()),
                                        args=[
                                            ast.JoinedStr([
                                                ast.Str(s=f"Would {args[0].s}: "),
                                                ast.FormattedValue(
                                                    value=args[1],
                                                    conversion=-1
                                                )
                                            ])
                                        ],
                                        keywords=[]
                                    )
                                )
                                new_body.append(print_stmt)
                node.body = new_body
            return node

    tree = ast.parse(code)
    modified_tree = PrintAdder().visit(tree)
    return ast.unparse(modified_tree)
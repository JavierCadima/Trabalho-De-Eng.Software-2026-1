import os
import sys
print('cwd', os.getcwd())
print('sys.path[0]', sys.path[0])
print('sys.path[:5]', sys.path[:5])
try:
    import models.venda as mv
    print('mv.__file__', mv.__file__)
    print('has VendaDTO', hasattr(mv, 'VendaDTO'))
    print('has ItemVenda', hasattr(mv, 'ItemVenda'))
    if hasattr(mv, 'VendaDTO'):
        print('VendaDTO', mv.VendaDTO)
    if hasattr(mv, 'ItemVenda'):
        print('ItemVenda', mv.ItemVenda)
except Exception:
    import traceback
    traceback.print_exc()

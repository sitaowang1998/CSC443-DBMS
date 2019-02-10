from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record
from scan import Scanner
from search import TableTreeSearch, IndexTreeSearch
from ranger import TableTreeRange, IndexTreeRange
from helper import get_root_page, print_count, get_entry, get_EmpID, get_last_name, print_entry, print_time


def find_name(dheader, db, root_page_no, name):
    """
    Find the name in the db.
    """
    scanner = Scanner(root_page_no, dheader, db)
    for rowid, record in scanner:
        if get_last_name(rowid, record) == name:
            print_entry(rowid, record)

def find_id(dheader, db, root_page_no, EmpID):
    rowid, record = TableTreeSearch(root_page_no, EmpID, dheader, db)
    print_entry(rowid, record)

def find_id_range(dheader, db, root_page_no, low, high):
    ranger = TableTreeRange(root_page_no, db, dheader, low, high)
    for rowid, record in ranger:
        empID = get_EmpID(rowid, record)
        if empID >= low and empID <= high:
            print_entry(rowid, record)


if __name__ == "__main__":
    fileName = "unclustered.db"
    print(fileName)
    db = open(fileName, 'rb')
    dheader = DHeader(db)
    root_page_no = get_root_page(dheader, db, "Employee")
    
    Page.clear_count()
    print("=" * 20)
    print("Finding employee with last name Rowe")
    find_name(dheader, db, root_page_no, "Rowe")
    print_count()
    print_time()
    print()

    Page.clear_count()
    print("=" * 20)
    print("Finding employee with EmpID 181162")
    find_id(dheader, db, root_page_no, 181162)
    print_count()
    print_time()
    print()

    Page.clear_count()
    print("=" * 20)
    print("Finding employee with EmpID between 171800 and 171899")
    find_id_range(dheader, db, root_page_no, 171800, 171899)
    print_count()
    print_time()
    print()



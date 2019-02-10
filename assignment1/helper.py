import os

from header import DHeader
from page import Page, BTreePage, FirstPage
from cell import Record

def get_root_page(dheader, db, name):
    """
    Return the root page of the database with name, None otherwise.
    """
    firstPage = FirstPage(dheader, db)
    for i in range(firstPage.cell_num):
        cell = firstPage.read_cell(db, i)
        record = Record(cell.cell.payload)
        if record.record[2] == name:
            return record.record[3]
    return None

def print_count():
    page_count, table_interior_count, table_leaf_count, index_interior_count, index_leaf_count = Page.get_count()
    print("Total pages: {}\n table interior pages: {}, table leaf pages: {}\n index interior pages: {}, index leaf pages: {}"\
        .format(page_count, table_interior_count, table_leaf_count, index_interior_count, index_leaf_count))

def get_entry(rowid, record):
    value = [record.record[i] for i in range(len(record.record))]
    if record.record[0] == None:
        value[0] = rowid
    return value

def get_EmpID(rowid, record):
    return get_entry(rowid, record)[0]

def get_first_name(rowid, record):
    return get_entry(rowid, record)[2].strip()

def get_last_name(rowid, record):
    return get_entry(rowid, record)[4].strip()

def get_middle_initial(rowid, record):
    return get_entry(rowid, record)[3].strip()

def print_entry(rowid, record):
    entry = get_entry(rowid, record)
    print("EmpID: {}, Name: {} {} {}".format(entry[0], entry[2].strip(), entry[3].strip(), entry[4].strip()))

def print_time():
    print("Total time to read pages: {} seconds".format(Page.get_time()))
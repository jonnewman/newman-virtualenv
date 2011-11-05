import sys
#sample sqlerror
'''
sql:'update [CustomerMembership] set referredby_id=?,auto_renew=?,lastmodifieddate=?,disabled=?,loyalty_closed=?,renewdate=?,startdate=?,creditdate_monthly=?,_prev_renewdate=?,createdby=?,createddate=?,customer_id=?,card_issued=?,primary_id=?,_prev_enddate=?,remarks=?,enddate=?,direct_debit=?,_prev_primary_id=?,creditdate_qtly=?,gender=?,membership_id=?,creditdate_weekly=?,lastmodifiedby=?,pmts_remaining=?,repldate=?,pmt_dom=? where id=?'
params:(None, 'False', '2011-11-04 12:47:03.000', 'False', 'False', '2010-11-26 16:51:00.000', '2007-09-28 09:23:00.000', '2011-11-04 12:47:00.000', '2010-11-26 16:51:00.000', 'web', '2007-09-28 09:23:09.000', '3F47C664-C637-4773-9B98-5C0EF2BD169D', None, '100E21D1-06E3-11E1-94F3-00199926BBBA', '2011-11-28 15:26:00.000', None, '2011-11-28 15:26:00.000', 'False', None, '2011-11-04 12:47:00.000', None, '56c', '2011-11-04 12:47:00.000', 'system', '0', '2011-11-05 16:04:18.000', None, 'CE9F8305-5418-419C-95E9-0899617BFF5F')
'''

def main():
    error_log = open(sys.argv[1]).read()
    sql, params = error_log.splitlines()
    sql = sql.replace('=?,', '=%s,\n')
    sql = sql.replace('=?', '=%s')
    params = params[len('params:'):]
    params = eval(params)
    print sql %params

if __name__ == '__main__':
    main()

import xmlrpclib
import hashlib
from xml.etree import ElementTree

user = 'system'
passwd = hashlib.md5('MAc8E3he').hexdigest()


def get_external_uri():
    venue_uri_dict = {}
    url = 'http://cityscreen.clients.newmanonline.org.uk:8002'
    branch_server = xmlrpclib.Server(url)
    venue_id_list = ['bath','bmnt','BSE','camb','cph','doyb','edbg','fact','gate','gnw','hlsh','nor','oxfd','rgl','ritz','se','soa','xtr','york']
    sess, _ = branch_server.user.login(user, passwd)
    xml = branch_server.venue.get(sess, venue_id_list)
    tree = ElementTree.fromstring(xml.encode('utf-8'))
    venue_list = tree.findall('Venue')
    for venue in venue_list:
        venue_uri_dict[venue.attrib['id']] = venue.attrib['external_uri']
    return venue_uri_dict

def run_venue_task(venue_uri):
    venue_server = xmlrpclib.Server(venue_uri)
    sess, _ = venue_server.user.login(user, passwd)
    #venue_server.tasks.createDirectDebitAccounts(sess)
    venue_server.tasks.chargeDirectDebitAccounts(sess)
    #venue_server.tasks.renewDirectDebitCustomerMemberships(sess)
    #venue_server.tasks.calcDirectDebitNextChargeDate(sess)

if __name__ == '__main__':
    venue_uri_dict = get_external_uri()
    print venue_uri_dict
    for venue_id in venue_uri_dict:
        print venue_id
        if 1:
            try:
                run_venue_task(venue_uri_dict[venue_id])
            except:
                pass

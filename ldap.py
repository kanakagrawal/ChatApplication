import ldap3
address = "ldap://cs252lab.cse.iitb.ac.in:389"
con = ldap3.initialize(address)
base_dn = "dc=cse.iitb.ac,dc=in"
con.protocol_version = ldap3.VERSION3
USERNAME = "shaan"
PASSWORD = "skhbfeif"
search_filter = "(uid=USERNAME)"
result = con.search_s(base_dn, ldap3.SCOPE_SUBTREE, search_filter, None)  
user_dn = result[0][0]  # get the user DN
con.simple_bind_s(user_dn, "PASSWORD")
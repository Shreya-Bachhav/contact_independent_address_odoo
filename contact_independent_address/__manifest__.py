{
    'name': 'Contact Independent Address',
    'version': '19.0.1.0.0',
    'summary': 'Keep child contact addresses independent from their parent company.',
    'description': """
Stops Odoo from automatically copying a parent company address onto child
contacts, and from pushing a child contact address back to the parent company.
This allows each child contact to maintain its own address independently.
    """,
    'author': 'Shreeram Solar',
    'category': 'Contacts',
    'depends': ['contacts'],
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

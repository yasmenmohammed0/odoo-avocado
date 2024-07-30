{
    'name': "Mottasl events",
    'author': "Twerlo",
    'website': "www.twerlo.com",
    'depends': ['base','web',"account","crm","sale"],
    'summary': 'Use Mottasl WA messaging to track different events',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'auto_install':False,
    'data': [
        'views/res.xml',
    ],
    'post_init_hook': 'post_init_hook',
}

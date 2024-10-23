{
    "name"          : "Stock Report",
    "version"       : "17.0.0.1.0",
    "author"        : "Miftahussalam",
    "website"       : "https://blog.miftahussalam.com",
    "category"      : "Reporting",
    "license"       : "LGPL-3",
    "support"       : "me@miftahussalam.com",
    "summary"       : "Download report in excel format",
    "description"   : """
        Stock Report Excel
    """,
    "depends"       : [
        "product",
        "stock",
    ],
    "data"          : [
        "security/ir.model.access.csv",
        "wizard/ms_report_stock_wizard.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [
        "static/description/images/main_screenshot.png",
    ],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}
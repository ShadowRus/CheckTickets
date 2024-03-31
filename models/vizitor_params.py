def visitor_data_type2(code_label,surname,name,org,barcode,city):
    dict_new= {
        "document": {
            "name": "documents",
            "protocol": "atolmsk",
            "details": [
                {
                    "type": "task",
                    "code": code_label,
                    "count": "2",
                    "values": [
                        {
                            "id": "Surnam",
                            "data": surname
                        },
                        {
                            "id": "Name",
                            "data": name
                        },
                        {
                            "id": "org",
                            "data": org
                        },
                        {
                            "id": "Barcode",
                            "data": barcode
                        },
                        {
                            "id": "City",
                            "data": city
                        }
                    ]
                }
            ]
        }
    }
    return dict_new


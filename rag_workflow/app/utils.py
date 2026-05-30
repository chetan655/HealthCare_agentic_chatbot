

from app.schema.schema import State


def check_query_category(state: State):
    
    category = state.get("category", "")

    if category == "ocr":
        return "ocr"
    elif category == "nearby_hospitals":
        return "find_nearby_hospitals"
    elif category == "emergency":
        return "emergency"
    else:
        return "general"
    
def route_after_tools(state: State):
    
    category = state.get("category", "")

    if category == "ocr":
        return "ocr_formatter"
    elif category == "nearby_hospitals":
        return "hospital_formatter"
    # elif category == "emergency":
    #     return "emergency"
    else:
        return "general"
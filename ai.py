import json
import boto3
import logging

logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

def ai_function(lst): 
    """
    Takes in a list of dictionaries
    Returns the list of dictionaries with each dictionary containing an additional key "relevance_score",
    whose value is a list
    """

    client = boto3.client('runtime.sagemaker')
    
    for dic in lst:
        sentence_chunk = dic["sentence_chunk"]
        relevance_score = []
        input_data = {
            "instances" : []
        }
        for i in range(len(dic["title"])):
            if i in range(len(dic["synopsis"])):
                search_result = dic["title"][i] + dic["synopsis"][i]
                input_data["instances"].append({
                    "sentence1" : sentence_chunk,
                    "sentence2" : search_result
                })
                # input_data = {
                #     "sentence1" : sentence_chunk,
                #     "sentence2" : search_result
                # }
                # To send by instance, unindent the invokation command so it invokes every dictionary
        response = client.invoke_endpoint(
            EndpointName='pytorch-inference-2020-08-30-08-57-27-011', 
            Body=json.dumps(input_data))
        response_body = response['Body'].read()
        
                # similarity = response_body.decode('utf-8')
                # relevance_score.append(int(similarity))

        relevance_score_string = response_body.decode('utf-8')
        logger.info("AI output string = " + relevance_score_string)
        relevance_score_string = relevance_score_string.strip('[')
        relevance_score_string = relevance_score_string.strip(']')
        relevance_score = relevance_score_string.split(", ")
        dic["relevance_score"] = relevance_score

        logger.info("AI output = " + str(relevance_score))

    return lst
from flask import Flask, request
from flask import send_file

import analytics_bot_langchain


app = Flask(__name__)

@app.route('/query', methods = ['GET'])
def query():
    dataset_ids = request.args.get('dataset_ids', None)
    format = request.args.get('format', 'json')
    if format == 'json':
        agent = analytics_bot_langchain.get_agent(dataset_ids=dataset_ids)
        question = request.args.get('question', default='Perform EDA')
        response = agent(question)
        intermediate_steps = response['intermediate_steps']
        first_result = intermediate_steps[0][-1]
        return first_result
    else:
        agent = analytics_bot_langchain.get_agent(dataset_ids=dataset_ids)
        question = request.args.get('question', default='Perform EDA')
        response = agent(question)
        intermediate_steps = response['intermediate_steps']
        first_result = intermediate_steps[0][-1]
        return send_file('outputs/result.png', mimetype='image/gif')


if __name__ == '__main__':
   app.run(
       port = 8000,
       debug = True
    )

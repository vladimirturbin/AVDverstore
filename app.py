from flask import Flask, render_template, request, make_response
import json
import urllib.request
import urllib.response
from datetime import datetime

app = Flask(__name__)

data_file = 'data.json'
AVD_links = {
    'insider': [
        'https://go.microsoft.com/fwlink/?linkid=2099432',
        'https://go.microsoft.com/fwlink/?linkid=2099433'
    ],

    'release': [
        'https://go.microsoft.com/fwlink/?linkid=2099065',
        'https://go.microsoft.com/fwlink/?linkid=2098963'
    ]
}


def save_new_version():
    # here we load 'data' from file', try to add new links and save back to file
    with open(data_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for link_type in AVD_links.keys():
        new_links = get_current_urls(AVD_links[link_type])
        append_only_new_urls(data, new_links, link_type)

    with open(data_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return


def append_only_new_urls(data, new_links, links_type):
    # here we will check if current links presented in 'data' yet or not
    for link in new_links:
        link['is_new'] = 1
        for stored_link in data.values():

            if stored_link['links_type'] == links_type and \
                    stored_link['version'] == link['version'] and \
                    stored_link['platform'] == link['platform']:
                # link will get 'is_new' parameter = 0 if there is same link in 'data'
                link['is_new'] = 0

    for link in new_links:

        if link['is_new'] == 1:
            del link['is_new']
            link['links_type'] = links_type
            date_now = datetime.now()
            link['date'] = date_now.strftime("%Y-%m-%d, %H:%M:%S")
            data[str(int(max(data.keys(), key=int)) + 1)] = link
    return


def get_current_urls(urls_load_list):
    # here we will download current urls from links stored in AVD_links
    distro_data = []
    for url in urls_load_list:
        response = urllib.request.urlopen(url)
        distro_data.append(json.loads(response.read()))
    return distro_data


@app.route('/')
def main_table():
    with open(data_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return render_template('main_table.html', data=data)


@app.route('/xml')
def xml_render():
    with open(data_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    template = render_template('WVDClientSupport.xml', data=data, ver=request.args.get('ver'))
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response


@app.route('/reg')
def reg_render():
    with open(data_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    template = render_template('update.reg', data=data, ver=request.args.get('ver'), addr=request.remote_addr)
    response = make_response(template)
    response.headers['Content-Type'] = 'text/plain'
    return response


if __name__ == '__main__':
    app.run()

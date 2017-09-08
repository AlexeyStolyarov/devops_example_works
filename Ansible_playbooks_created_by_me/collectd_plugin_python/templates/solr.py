import time
import requests
import json
from pyjolokia import Jolokia

try:
        import collectd
except:
        import collectd_tools.collectd_mockup as collectd


class SolrConfig:
    plugin_name = 'solr'
    url = 'http://127.0.0.1:8983'
    jolokia_url = 'http://127.0.0.1:8778/jolokia/'

solr_config = SolrConfig()

class SolrIndex:
    name = ''
    indexSizeInBytes = 0
    percentile95RequestTime = 0
    percentile99RequestTime = 0
    requests = ''
    update_commits = 0
    update_autocommits = 0
    update_soft_autocommits = 0
    update_docs_pending = 0
    update_cumulative_adds = 0
    update_cumulative_deletes_by_id = 0
    update_cumulative_deletes_by_query = 0
    update_cumulative_errors = 0
    searcher_num_docs = 0
    searcher_deleted_docs = 0
    searcher_index_version = 0


    def __init__(self):
        pass

class SolrKeyValue:
    key = ''
    value = 0
    type = 'gauge'

    def __init__(self, key='', value=0, type='gauge'):
        self.key = key
        self.value = value
        self.type = type


def config_callback(config):
    collectd.info('config parse: {0}: key: {1}; values: {2};'.format(solr_config.plugin_name, config.key, ' '.join(config.values)))
    # invoke callback for children and return
    if config.key == 'Module' and config.values[0] == solr_config.plugin_name and config.parent is None:
        for i in config.children:
            config_callback(i)
        return

    known_keys = ['solr_url', 'jolokia_url']
    if config.key not in known_keys:
        raise Exception('Unknown config option: %s' % config.key)

    if config.key == 'solr_url':
        solr_config.url = config.values[0]

    if config.key == 'jolokia_url':
        solr_config.jolokia_url = config.values[0]


def collect_common_data():
    result = []

    j4p = Jolokia(solr_config.jolokia_url)
    #j4p.add_request(type='read', mbean='solr:id=NativeTrackerStats,type=NativeTrackerStats')
    #data = j4p.getRequests()
    #print(json.dumps(data, indent=4, separators=(',', ': ')))
    #exit(1)

    data = j4p.request(type='read', mbean='solr:id=NativeAllocatorStats,type=NativeAllocatorStats')
    result.append(SolrKeyValue('numAlloc', data['value']['numAlloc'], 'derive'))
    result.append(SolrKeyValue('numFree', data['value']['numFree'], 'derive'))
    result.append(SolrKeyValue('totalFreedMemoryInBytes', data['value']['totalFreedMemoryInBytes'], 'derive'))
    result.append(SolrKeyValue('activeAllocatedMemoryInBytes', data['value']['activeAllocatedMemoryInBytes']))
    result.append(SolrKeyValue('totalAllocatedMemoryInBytes', data['value']['totalAllocatedMemoryInBytes'], 'derive'))

    data = j4p.request(type='read', mbean='solr:id=NativeTrackerStats,type=NativeTrackerStats')
    result.append(SolrKeyValue('registeredThreads', data['value']['registeredThreads']))
    result.append(SolrKeyValue('trackedObjects', data['value']['trackedObjects']))
    result.append(SolrKeyValue('handedOffObjects', data['value']['handedOffObjects']))

    return result


def collect_data():
    http_timeout = 1
    cur_time = int(time.time())

    r = requests.get('{url}/solr/admin/cores?wt=json&indexInfo=false&_={time}'.format(url=solr_config.url, time=cur_time),
                     timeout=http_timeout)
    if r.status_code != 200:
        raise RuntimeError('Api response(cores) return non 200 status')
    data = r.json()

    indexes = []
    for k in data['status'].iterkeys():
        indexes.append(k)

    result = []
    for k in indexes:
        r = requests.get('{url}/solr/{index}/admin/mbeans?stats=true&cat=CORE&cat=QUERYHANDLER&cat=UPDATEHANDLER&wt=json&_={time}'.format(url=solr_config.url, index=k, time=cur_time),
                         timeout=http_timeout)
        if r.status_code != 200:
            raise RuntimeError('Api response(cores) return non 200 status')
        data = r.json()

        index = SolrIndex()
        index.name = k
        count = 0
        for v in data['solr-mbeans']:
            if count > 3:
                break
            if 'core' in v:
                index.indexSizeInBytes = v['core']['stats']['indexSizeInBytes']
                count += 1
            if 'searcher' in v:
                index.searcher_num_docs = v['searcher']['stats']['numDocs']
                index.searcher_deleted_docs = v['searcher']['stats']['deletedDocs']
                index.searcher_index_version = v['searcher']['stats']['indexVersion']
                count += 1
            if 'search' in v:
                index.requests = v['search']['stats']['requests']
                index.percentile95RequestTime = v['search']['stats']['95thPcRequestTime']
                index.percentile99RequestTime = v['search']['stats']['99thPcRequestTime']
                count += 1
                continue
            if 'updateHandler' in v:
                index.update_commits = v['updateHandler']['stats']['commits']
                index.update_autocommits = v['updateHandler']['stats']['autocommits']
                index.update_soft_autocommits = v['updateHandler']['stats']['soft autocommits']
                index.update_docs_pending = v['updateHandler']['stats']['docsPending']
                index.update_cumulative_adds = v['updateHandler']['stats']['cumulative_adds']
                index.update_cumulative_deletes_by_id = v['updateHandler']['stats']['cumulative_deletesById']
                index.update_cumulative_deletes_by_query = v['updateHandler']['stats']['cumulative_deletesByQuery']
                index.update_cumulative_errors = v['updateHandler']['stats']['cumulative_errors']
                count += 1
                continue
        result.append(index)
    return result


def get_metric():
    # KEY PLANING: hostname / plugin - plugin_instance / type - type_instance
    # * plugin = solr
    # * plugin_instance = <metric>
    # * type = guage|derive
    # * type_instance = <index>
    metric = collectd.Values()
    metric.interval = 60
    metric.plugin = solr_config.plugin_name
    metric.plugin_instance = 'index'
    metric.type = 'gauge'

    return metric


def read_callback(data=None):

    collect = []
    try:
        collect = collect_data()
    except requests.exceptions.RequestException:
        exit(1)
    #except Exception:
    #    exit(2)

    for v in collect:
        collectd.debug(solr_config.plugin_name + ' name: ' + v.name)
        #collectd.debug(solr_config.plugin_name + ' 95: {0:f}'.format(v.percentile95RequestTime))
        #collectd.debug(solr_config.plugin_name + ' 99: {0:f}'.format(v.percentile99RequestTime))
        #collectd.debug(solr_config.plugin_name + ' requests: {0:d}'.format(v.requests))
        #collectd.debug(solr_config.plugin_name + ' indexSizeInBytes: {0:d}'.format(v.indexSizeInBytes))

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'requests'
        metric.values = (v.requests,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.plugin_instance = 'ptl95ReqTime'
        metric.values = (v.percentile95RequestTime,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.plugin_instance = 'ptl99ReqTime'
        metric.values = (v.percentile99RequestTime,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.plugin_instance = 'size'
        metric.values = (v.indexSizeInBytes,)
        metric.dispatch()

        # update
        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_commits'
        metric.values = (v.update_commits,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_autocommits'
        metric.values = (v.update_autocommits,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_soft_autocommits'
        metric.values = (v.update_soft_autocommits,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.plugin_instance = 'update_docs_pending'
        metric.values = (v.update_docs_pending,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_cumulative_adds'
        metric.values = (v.update_cumulative_adds,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_cumulative_deletes_by_id'
        metric.values = (v.update_cumulative_deletes_by_id,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_cumulative_deletes_by_query'
        metric.values = (v.update_cumulative_deletes_by_query,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'update_cumulative_errors'
        metric.values = (v.update_cumulative_errors,)
        metric.dispatch()

        # searcher
        metric = get_metric()
        metric.type_instance = v.name
        metric.plugin_instance = 'searcher_num_docs'
        metric.values = (v.searcher_num_docs,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'searcher_deleted_docs'
        metric.values = (v.searcher_deleted_docs,)
        metric.dispatch()

        metric = get_metric()
        metric.type_instance = v.name
        metric.type = 'derive'
        metric.plugin_instance = 'searcher_index_version'
        metric.values = (v.searcher_index_version,)
        metric.dispatch()

    collect = []
    try:
        collect = collect_common_data()
    except BaseException:
        exit(3)

    for v in collect:
        collectd.debug(solr_config.plugin_name + ' name: ' + v.key)

        metric = get_metric()
        metric.type_instance = 'solr'
        metric.type = v.type
        metric.plugin_instance = v.key
        metric.values = (v.value,)
        metric.dispatch()




collectd.register_config(config_callback)
collectd.register_read(read_callback)

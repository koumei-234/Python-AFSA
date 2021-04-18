import json
from collections import OrderedDict
import pprint



d = {"algo":{"dim":2,"population":10,"trytimes":3},
    "fish": {"visual":0.2, "step":0.3},
    "params": {"i":0,"iter":10}
}

pprint.pprint(d, width=40)
sd = json.dumps(d)

print(sd)

with open('/Users/ystk/Documents/AFSA/fish.json', 'w') as f:
    json.dump(d, f, indent=4)
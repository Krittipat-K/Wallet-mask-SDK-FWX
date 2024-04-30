data = {'AVAX':{'address':'0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7','decimal':18},
        'USDC':{'address':'0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E','decimal':6},
        'FWX':{'address':'0x9F0AfA63465606c4a9bD8543FF9FEDC7273F45d9','decimal':18},
        'SAVAX':{'address':'0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE','decimal':18},
        'COQ':{'address':'0x420FcA0121DC28039145009570975747295f2329','decimal':18},
        'GMX':{'address':'0x62edc0692BD897D2295872a9FFCac5425011c661','decimal':18},
        'JOE':{'address':'0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd','decimal':18},
        'PNG':{'address':'0x60781C2586D68229fde47564546784ab3fACA982','decimal':18},
        'QI':{'address':'0x8729438EB15e2C8B576fCc6AeCdA6A148776C0F5','decimal':18},
        'ETHe':{'address':'0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB','decimal':18},}
class T_Data:
    def __init__(self,name:str) -> None:
        self.name = name
        self.data = data
        pass
    def get_address(self):
        return self.data[self.name]['address']
    
    def get_decimal(self):
        return self.data[self.name]['decimal']

class revert_map:
    def __init__(self,address:str) -> None:
        self.address = address
        self.data = {data[i]['address']:i for i in data}
        pass
    def get_data(self):
        return self.data[self.address]
    
# if __name__ == "__main__":
#     G = revert_map('0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB')
#     print(G.get_data())
    
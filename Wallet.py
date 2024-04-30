from dotenv import load_dotenv
import os
load_dotenv()
from defi_sdk_py.avalanche_chain import ADDRESS as Avalanche_ADDRESS
from defi_sdk_py.avalanche_chain import AvalancheChainClient
from web3 import Web3, HTTPProvider, types
from web3.middleware import geth_poa_middleware
from Token_data import T_Data, revert_map,data
from defi_sdk_py.abi.IHelperFutureTrade import PositionData, PositionState
import json
import csv
import datetime
from defi_sdk_py.helper_future_trade import PythPriceFeeds

class Wallet:
    def __init__(self,private_key:str, native_coin:str, rpc_url:str = os.getenv('RPC_URL_avalanche')) -> None:
        self.__private_key:str = private_key
        self.rpc_url:str = rpc_url
        self.web3:Web3 = self.connect_to_web3()
        self.native_coin_balance = self.web3.eth.get_balance(self.address)
        self.native_coin = native_coin
        
        pass
    
    def connect_to_web3(self)->Web3:
        print("try connecting to chain")
        web3: Web3 = Web3(HTTPProvider(self.rpc_url))
        web3.eth.default_account = web3.eth.account.from_key(self.__private_key).address
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.address = web3.eth.default_account
        if web3.is_connected():
            print(f'Connected to {self.rpc_url}')
        else:
            raise ConnectionAbortedError(f"Failed to connect to {self.rpc_url}")
        return web3
    def get_min_gas_price(self)->float:
        
        return self.web3.eth.gas_price *10 ** -T_Data(self.native_coin).get_decimal()
    
    def checking_wallet_native_coin_balance(self)->float:
        
        return self.native_coin_balance *10 ** -T_Data(self.native_coin).get_decimal()
    
    def checking_wallet_coin_balance(self,coin:str)->float:
        
        with open('ierc20.json') as f:
            ierc20_abi = json.load(f)
            
        contract = self.web3.eth.contract(T_Data(coin).get_address(), abi=ierc20_abi)
        
        return contract.functions.balanceOf(self.address).call() * 10 ** -T_Data(coin).get_decimal()
    
    def connect_wallet_to_FWX(self, maxFeePerGas: float = 3000000, maxPriorityFeePerGas: float = 2000000) -> AvalancheChainClient:
        
        self.FWX_client:AvalancheChainClient = AvalancheChainClient(rpc_url=self.rpc_url,
                                                                    private_key=self.__private_key,
                                                                    address_const= Avalanche_ADDRESS,
                                                                    maxFeePerGas=self.get_min_gas_price()*10**T_Data(self.native_coin).get_decimal(),
                                                                    maxPriorityFeePerGas=maxPriorityFeePerGas)
        self.available_coin = list(data.keys())
        self.__pair = {'AVAX':['COQ','GMX','JOE','PNG','QI','SAVAX','ETHe'],
                     'USDC':['AVAX']} 
        self.available_pair_trade = [j+i for i in self.__pair for j in self.__pair[i]]
        self.default_FWX_NFT = self.FWX_client.get_default_membership(self.address)
        self.__columns_log = ['Timestamp', 'Ticker', 'Size']
        self.__map_coin_FWX:dict = {i:self.FWX_client.TOKEN.__getattribute__(i) if not(i in ['AVAX','ETHe']) else self.FWX_client.TOKEN.__getattribute__('W'+i) for i in self.available_coin}
        if not os.path.exists(f"Wallet_open_log.csv"):
            with open(f"Wallet_open_log.csv", 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.__columns_log)
                writer.writeheader()
                
        if not os.path.exists(f"Wallet_close_log.csv"):
            with open(f"Wallet_close_log.csv", 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.__columns_log)
                writer.writeheader()
        with open('address.json') as f:
            address = json.load(f)
        self.DEX_address = {address['ROUTER'][i]['ROUTER']:i for i in address['ROUTER']}
        pass
        
    def mint_FWX_NFT(self, referral_id:int = 0):
        
        self.FWX_client.mint(referal_id=referral_id)
        
        print('Successfully minted')
        
    def get_all_FWX_NFT_ID(self)->list[int]:
        
        self.my_FWX_NFT = self.FWX_client.get_nft_list(self.address).nft_list
        
        return self.my_FWX_NFT
    
    def set_current_FWX_NFT(self,NFT_ID:int = None):
        
        if NFT_ID == None:
            NFT_ID = self.default_FWX_NFT

        self.default_FWX_NFT = NFT_ID
        
        print('Successfully setting')
        
    def adding_collateral_FWX(self, underlying_token:str, collateral_token:str, amount:float, is_estimate: bool = False, gas: int = 0, gas_price: int = 0, nonce: int = 0, nft_id: int = None)-> dict:
        
        if nft_id is None:
            nft_id = self.default_FWX_NFT
        
        report:dict =  self.FWX_client.deposit_collateral(nft_id=nft_id,
                                                          collateral_token_address=self.__map_coin_FWX[collateral_token],
                                                          underlying_token_address=self.__map_coin_FWX[underlying_token],
                                                          amount=amount,
                                                          is_estimate=is_estimate,
                                                          gas=gas,
                                                          gas_price=gas_price,
                                                          nonce=nonce)
        
        return report
    
    def checking_collateral_FWX(self, underlying_token: str, collateral_token: str, nft_id: int = None) -> dict:
        
        if nft_id is None:
            nft_id = self.default_FWX_NFT
        pair_byte = self.FWX_client.pairs(
            collateral_token=T_Data(collateral_token).get_address(),
            underlying_token=T_Data(underlying_token).get_address()
        )
        
        # Get balance details for the specified NFT and pair byte
        detail = self.FWX_client.get_balance_details(nft_id, pair_byte)
        
        # Prepare the report with total, free, and used balances
        report = {
            'Total balance': detail.total_balance * 10**-T_Data(collateral_token).get_decimal(),
            'Free balance': detail.free_balance * 10**-T_Data(collateral_token).get_decimal(),
            'Used balance': detail.used_balance * 10**-T_Data(collateral_token).get_decimal()
        }
        
        return report
    
    def open_position_FWX(self, underlying_token: str, collateral_token: str, slip_page: float, is_long: bool, leverage: float, desired_price: float, size: float, is_estimate: bool = False, gas: int = 0, gas_price: int = 0, nonce: int = 0, nft_id: int = None) -> dict:
        
        if nft_id is None:
            nft_id = self.default_FWX_NFT
        
        # Call FWX client's open_position function to open the position
        report: dict = self.FWX_client.open_position(
            nft_id=nft_id,
            is_long=is_long,
            collateral_token=self.__map_coin_FWX[collateral_token],
            underlying_token=self.__map_coin_FWX[underlying_token],
            entry_price=desired_price,
            size=size,
            leverage=leverage,
            slip_page=slip_page,
            is_estimate=is_estimate,
            gas=gas,
            gas_price=gas_price,
            nonce=nonce
        )
        
        # Log the opening of the position to a CSV file
        today = int(datetime.datetime.now().timestamp() * 1000)
        with open(f"Wallet_open_log.csv", 'a', newline='') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames=self.__columns_log) 
            writer.writerow(dict(zip(self.__columns_log, [today, underlying_token + collateral_token, size])))
        
        return report
    
    def get_current_positions_FWX(self, nft_id: int = None) -> dict:
        
        if nft_id is None:
            nft_id = self.default_FWX_NFT
            
        current:list[PositionData] = self.FWX_client.get_all_active_positions(nft_id=nft_id)
        self.current_position_FWX = dict()
        
        for i in current:
            
            pos:int = i.position[0]
            is_long:bool = self.FWX_client.positions_states(nft_id=nft_id,pos_id=pos).isLong
            collateral = revert_map(i.position[1]).get_data()
            
            if is_long:
                underlying = revert_map(i.position[4]).get_data()
                size = i.position[6] * 10**-T_Data(underlying).get_decimal()
            else:
                underlying = revert_map(i.position[3]).get_data()
                size = -1*i.position[7] * 10**-T_Data(underlying).get_decimal()
                
            self.current_position_FWX[underlying+collateral] = {'ID': pos, 'Size': size}
            
        return self.current_position_FWX
    def close_position_FWX(self, pos_id: int, closing_size: float, nft_id: int = None, is_estimate: bool = False, gas: int = 0, gas_price: int = 0, nonce: int = 0):
            
        if nft_id is None:
            nft_id = self.default_FWX_NFT
            
        report = self.FWX_client.close_position(
            nft_id=nft_id,
            pos_id=pos_id,
            closing_size=closing_size,
            is_estimate=is_estimate,
            gas=gas,
            gas_price=gas_price,
            nonce=nonce
        )
        today = int(datetime.datetime.now().timestamp() * 1000)
        D = self.FWX_client.positions_states(nft_id=nft_id, pos_id=pos_id)
        underlying_token = revert_map(self.FWX_client.pairs_by_byte(D.pairByte).pair1).get_data()
        collateral_token = revert_map(self.FWX_client.pairs_by_byte(D.pairByte).pair0).get_data()
        with open(f"Wallet_close_log.csv", 'a', newline='') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames=self.__columns_log) 
            writer.writerow(dict(zip(self.__columns_log, [today, underlying_token + collateral_token, closing_size])))
        
        return report
    
    def close_all_position_FWX(self, nft_id: int = None, is_estimate: bool = False, gas: int = 0, gas_price: int = 0, nonce: int = 0):
            
        if nft_id is None:
            nft_id = self.default_FWX_NFT
            
        data = self.get_current_positions_FWX(nft_id)
        report = []
        for i in data:
            report.append(self.close_position_FWX(
                pos_id=data[i]['ID'],
                closing_size=abs(data[i]['Size']),
                nft_id=nft_id,
                is_estimate=False,
                gas=0,
                gas_price=0,
                nonce=0
            ))
        
        return report
    
    # def get_required_collateral_FWX(self,underlying:str,collateral:str,is_long:bool,contract_size:float,leverage:int,desired_price:float,slip_page:float,nft_id:int = None)->dict:
        
    #     if nft_id is None:
    #         nft_id = self.default_FWX_NFT
            
    #     pair_byte = self.FWX_client.pairs(collateral_token=T_Data(collateral).get_address(),
    #                                       underlying_token=(T_Data(underlying).get_address()))
            
    #     report = self.FWX_client.get_required_collateral(nft_id=nft_id,
    #                                                      pair_byte=pair_byte,
    #                                                      is_long=is_long,
    #                                                      contract_size=contract_size,
    #                                                      leverage=leverage,
    #                                                      expected_rate=desired_price,
    #                                                      slip_page=slip_page)
        
    #     return {f'{underlying+collateral} price':report[0],
    #             'require collateral':report[1]}
        
    def get_max_contract_size_FWX(self,underlying:str,collateral:str,is_long:bool,leverage:int,desired_price:float,slip_page:float,nft_id:int = None)->dict:
        
        if nft_id is None:
            nft_id = self.default_FWX_NFT
            
        pair_byte = self.FWX_client.pairs(collateral_token=T_Data(collateral).get_address(),
                                          underlying_token=(T_Data(underlying)).get_address())
        
        report = self.FWX_client.get_max_contract_size(nft_id=nft_id,
                                                       pair_byte=pair_byte,
                                                       is_long=is_long,
                                                       leverage=leverage,
                                                       expected_rate=desired_price,
                                                       slip_page=slip_page)
        
        return report*10**-T_Data(underlying).get_decimal()
    
    def get_destination_DEX_FWX(self,swap_size:float,underlying:str,collateral:str,is_long:bool)->dict:
        
        if is_long:
            source = collateral
            destination = underlying
        else:
            source = underlying
            destination = collateral
        
        report = self.FWX_client.get_router_for_swap(contract_size_in_usd=1,
                                                     swap_size_output=swap_size,
                                                     source_token=self.__map_coin_FWX[source],
                                                     destination_token=self.__map_coin_FWX[destination])
        FEE = dict(zip(report.routers,report.swap_fees))
        
        return {'DEX':self.DEX_address[report.target_router],'Fee':FEE[report.target_router]*10**-T_Data(self.native_coin).get_decimal()}
    
    def get_price_form_Pyth(self)->dict:
        
        raw_price = PythPriceFeeds()
        coin = ['USDC','AVAX','ETHe']
        report = dict()
        for i in range(len(coin)):
            report[coin[i]] = {'Price':int(raw_price[i]['price'])*10**int(raw_price[i]['expo']),
                               'UNIX time':int(raw_price[i]['publish_time'])}
            
        return report
    
    

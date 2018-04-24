from sqlalchemy import desc, or_

from token_state_relational_mapper.mapper.database import Token, TokenHolder, Transfer, get_session
from token_state_relational_mapper.mapper.utils import convert_to_real_value_string


def get_token(contract_address):
    session = get_session()
    name, changed_in_block, total_supply, created, destroyed, decimals = \
        session.query(Token.name,
                      Token.last_changed_in_block,
                      Token.total_tokens_supply,
                      Token.total_tokens_created,
                      Token.total_tokens_destroyed,
                      Token.decimals) \
            .filter_by(address=contract_address) \
            .first()

    return {
        'contract_address': contract_address,
        'name': name,
        'lastChangedInBlock': changed_in_block,
        'total_supply': convert_to_real_value_string(total_supply, decimals),
        'total_created': convert_to_real_value_string(created, decimals),
        'total_destroyed': convert_to_real_value_string(destroyed, decimals)
    }


def get_top_token_holders(contract_address, number_of_top):
    def holder_to_dictionary(holder, decimals):
        return {
            'address': holder.address,
            'last_changed_in_block': holder.last_changed_in_block,
            'balance': convert_to_real_value_string(holder.balance, decimals),
            'turnover': convert_to_real_value_string(holder.token_turnover, decimals)
        }

    session = get_session()
    token_id, token_name, token_address, token_total_supply, token_decimals = session.query(Token.id, Token.name,
                                                                                            Token.address,
                                                                                            Token.total_tokens_supply,
                                                                                            Token.decimals).filter_by(
        address=contract_address).first()

    holders = session.query(TokenHolder).filter(TokenHolder.held_token_id == token_id).order_by(
        desc(TokenHolder.balance)).limit(number_of_top).all()

    return {
        'token_name': token_name,
        'token_address': token_address,
        'token_total_supply': convert_to_real_value_string(token_total_supply, token_decimals),
        'holders': list(map(lambda h: holder_to_dictionary(h, token_decimals), holders))
    }


def get_transfers(contract_address, wallet_address):
    session = get_session()

    token_id = session.query(Token.id).filter_by(address=contract_address).first()
    transfers = session.query(Transfer).filter(Transfer.token_id == token_id,
                                               or_(Transfer.from_address == wallet_address,
                                                   Transfer.to_address == wallet_address)).all()

    return [{
        'amount': str(transfer.amount),
        'tx_hash': transfer.tx_hash,
        'to_address': transfer.to_address,
        'from_address': transfer.from_address
    } for transfer in transfers]

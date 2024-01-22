from marshmallow import Schema, fields, validate, post_load


class DeployPOSTRequestSchema(Schema):
    """
    Schema for POST request to /deploy
    """
    coinbase_api_key = fields.String(required=True)
    coinbase_api_secret = fields.String(required=True)
    discord_webhook = fields.String(required=True)
    asset_id = fields.String(required=True)
    run_interval = fields.Integer(default=60)  # TODO: Add tag to the .user_env file
    run_indefinitely = fields.Boolean(default=True)  # TODO: Add tag to the .user_env file
    fixed_order_size = fields.Float(required=True)
    buy_order_cash = fields.Float(required=True)
    run_seed = fields.Boolean(default=True)
    percent_profit_min = fields.Float(required=True)
    buy_only = fields.Boolean(default=False)
    sell_only = fields.Boolean(default=False)
    accumulate_asset = fields.Boolean(default=False)
    accumulate_cash = fields.Boolean(default=True)

    @post_load
    def format_request(self, data, **kwargs) -> dict:

        # Fields in .user_env file that are to be replaced with user values
        user_env_fields = [
            "<USER-API-KEY>",
            "<USER-API-SECRET>",
            "<USER-DISCORD-WEBHOOK-URL>",
            "<USER-ASSET-ID>",
            "<USER-FIXED-ORDER-SIZE>",
            "<USER-BUY-ORDER-CASH>",
            "<USER-RUN-SEED>",
            "<USER-PERCENT-PROFIT-MIN>",
            "<USER-BUY-ONLY>",
            "<USER-SELL-ONLY>",
            "<USER-ACCUMULATE-ASSET>",
            "<USER-ACCUMULATE-CASH>"
        ]

        string_data = {key: str(value) for key, value in data.items()}
        combined_data = {**self.dump(self), **string_data}
        formatted_dict = {
            user_env_fields[0]: combined_data["coinbase_api_key"],
            user_env_fields[1]: combined_data["coinbase_api_secret"],
            user_env_fields[2]: combined_data["discord_webhook"],
            user_env_fields[3]: combined_data["asset_id"],
            user_env_fields[4]: combined_data["fixed_order_size"],
            user_env_fields[5]: combined_data["buy_order_cash"],
            user_env_fields[6]: combined_data["run_seed"],
            user_env_fields[7]: combined_data["percent_profit_min"],
            user_env_fields[8]: combined_data["buy_only"],
            user_env_fields[9]: combined_data["sell_only"],
            user_env_fields[10]: combined_data["accumulate_asset"],
            user_env_fields[11]: combined_data["accumulate_cash"]
        }
        return {"user_env": formatted_dict, "asset_id": combined_data["asset_id"]}


class KillDELETERequestSchema(Schema):
    """
    Schema for POST request to /kill
    """
    bot_id = fields.String(required=True)


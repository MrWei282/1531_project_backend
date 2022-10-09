1. name_first and name_last will be stored the same as argument, that is, it can include non-alphanumeric characters, e.g. if name_first is given as "And!rew?", it will be stored exactly as "And!rew?", regardless, handle will still be include casted-to-lowercase alphanumeric name_first and name_last concatenated. This assumption is to fit names from other language

2. channel creator is a member of the channel owner

3. auth_user_id and channel_id starts from 1

4. InputError for channel_invite will raise before AccessError in some scenarios, e.g. when both auth_user_id and u_id are not found to be member of the channel.

5. Argument with suffix id, e.g. auth_user_id and u_id are assumed to always be integer type, and argument with suffix _is, e.g. is_public is assumed to be boolean value
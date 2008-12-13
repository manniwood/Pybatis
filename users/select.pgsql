select username as "USERNAME",
       password as "PASSWORD"
  from users
 where 1 = 1
{% if ID is present %}
   and id = cast(%(ID)s as bigint)
{% endif %}
{% if USERNAME is present %}
   and username like %(USERNAME)s
{% endif %}
{% if PASSWORD is present %}
   and password = %(PASSWORD)s
{% endif %}



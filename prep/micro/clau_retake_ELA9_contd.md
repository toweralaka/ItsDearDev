Let's clear these up one at a time — these are actually two versions of the same underlying question, plus a separate one about file structure.

## 1 & 2. How does the frontend get exactly the fields it asks for (one or many)?

There are two layers to this answer — give the first, and if Zara pushes further, give the second.

### Layer 1: The basic answer — a serializer as a fixed contract

By default, an API endpoint doesn't return "whatever's in the database" — it returns whatever the **serializer** explicitly names as its fields. The serializer is an allow-list, not a mirror of the model:

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email"]   # ONLY these go out, regardless of what's on the model
```

If the model also has `password_hash`, `is_staff`, `internal_notes` — none of that leaks, because the serializer never mentions it. This is "the frontend gets exactly what the endpoint promises," which is the answer for a fixed-shape API.

### Layer 2: The harder version — the frontend picks *which* fields, dynamically

If the actual question is "the client wants to choose a *different* subset of fields on each request" (like `GET /users/5?fields=name,email` vs `GET /users/5?fields=name,email,phone`), you need field selection built in:

```python
class DynamicFieldsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        requested_fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if requested_fields is not None:
            allowed = set(requested_fields)
            for field_name in set(self.fields) - allowed:
                self.fields.pop(field_name)   # remove anything not requested

class UserSerializer(DynamicFieldsSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "phone", "address"]  # the FULL allow-list

# in the view:
def get(self, request, pk):
    user = User.objects.get(pk=pk)
    fields_param = request.query_params.get("fields")   # e.g. "name,email"
    requested = fields_param.split(",") if fields_param else None
    serializer = UserSerializer(user, fields=requested)
    return Response(serializer.data)
```

**The critical security detail to say out loud:** the client can only ever narrow the fields down from the serializer's pre-defined list — they can never request something that isn't already an allowed field on the serializer. You're filtering a safe list down, never letting the client name arbitrary model attributes.

**Say this:** *"The serializer defines the full universe of fields that are ever allowed to leave the API. If the frontend needs to request a specific subset — whether that's one field or several — I let it pass a `fields` parameter, and the serializer removes anything not requested from that pre-approved list. The client narrows down an allow-list; it never gets to name something outside it."*

🧒 **Like I'm 9:** The serializer is a menu — you can only order what's printed on it, never something from the kitchen that isn't listed. If you just want the appetizer and not the whole meal, you can say "just the appetizer, please" — but you can never ask for something that was never on the menu in the first place.

---

## 3. Django: where does internal business logic go vs. calls to external services?

This is a **file/module separation** question, and there's a standard answer:

| Concern | File | What lives there |
|---|---|---|
| Data shape & simple rules | `models.py` | Fields, simple validation (`clean()`), simple computed properties that only need the model's own data |
| Internal business logic | `services.py` (or a `services/` package) | The actual rules — "what happens when an order is placed," "how a refund is calculated" — orchestrating models and other functions |
| External API calls | `clients.py` / `integrations.py` (or a dedicated `integrations/` package, e.g. `integrations/stripe_client.py`) | Thin wrappers around third-party calls — Stripe, SendGrid, a shipping provider's API |
| Request/response handling | `views.py` | Parses the HTTP request, calls the service layer, returns a response |
| API contract | `serializers.py` | Defines exactly what data goes in/out |

**Why external calls get their *own* file, separate from services.py:** it isolates your business logic from any specific vendor. `services.py` calls something like `stripe_client.charge(amount, customer_id)` — it doesn't know or care that this is implemented with `requests.post()` under the hood. Two direct benefits: (1) if you switch payment providers, you only touch `clients.py`, not every place that charges a customer; (2) in tests, you mock the client object, never the actual `requests` library or network call.

```python
# integrations/stripe_client.py — ONLY knows about talking to Stripe
def charge_customer(customer_id, amount):
    response = requests.post("https://api.stripe.com/charge", json={...})
    return response.json()

# services.py — ONLY knows about your business rules, not about Stripe specifically
from integrations.stripe_client import charge_customer

def process_order_payment(order):
    result = charge_customer(order.customer_id, order.total)
    if result["status"] == "success":
        order.mark_paid()
    return result
```

**Say this:** *"Models hold data and simple validation. Business logic lives in a services module, which orchestrates the actual rules. External API calls get their own separate module — a thin client wrapper — so the business logic never talks to a third-party API directly. That separation means I can swap providers or mock the client in tests without touching my actual business rules."*

🧒 **Like I'm 9:** The model is the pantry — it just stores ingredients. The service layer is the recipe — it decides what steps happen and in what order. The external client is like a delivery driver you call when you need something from outside the kitchen (like Stripe or an email provider) — the recipe just says "go get me a payment confirmation," it doesn't care whether the driver takes a car or a bike to get it.

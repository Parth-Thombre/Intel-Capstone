"""Persistent state and repository implementations.

Future repositories store deliveries, bin custody, observations, reservations,
events and commands. State changes, processed event IDs and pending outgoing
commands must share a transaction as specified in docs/ARCHITECTURE.md.

Database connections, schemas and migrations are not implemented here yet.
Importing this package creates no database or filesystem state.
"""

You are a Senior AI Architect and Full Stack Engineer.

We are participating in AgentCon 2026.

IMPORTANT:

DO NOT create a new project from scratch.

I already have a Medical-Legal AI project.

Your job is to create a NEW project inside a NEW folder by REUSING and REFACTORING as much existing code as possible.

Reuse at least 80-90% of the existing project.

Copy only reusable modules.

Do NOT rewrite working code.

Do NOT redesign the UI.

Keep the existing theme, layout, dashboard, colors, and components.

Only modify the workflow and features to satisfy the hackathon problem statement.

====================================================

PROJECT NAME

MedComply AI

Healthcare Compliance & Governance Intelligence Agent

====================================================

HACKATHON PROBLEM

Compliance & Governance Intelligence Agent

The solution must satisfy

✔ AI Agents

✔ Agentic Workflow

✔ Workflow Automation

✔ Decision Support

✔ Enterprise Intelligence

✔ RAG

✔ Multi-Agent Collaboration

✔ LangGraph

====================================================

CURRENT PROJECT HAS

✔ PDF Upload

✔ Medical Chronology

✔ Draft Generator

✔ RAG

✔ ChromaDB

✔ Embeddings

✔ Vector Search

✔ Medical Rules

✔ Laws

✔ Judgements

✔ Hospital Templates

✔ Existing Dashboard

✔ Existing Backend

✔ Existing Frontend

✔ Existing Prompting

Reuse everything.

====================================================

CURRENT DATA

Use the existing folders.

Do NOT create fake datasets.

Use

medical_rules/

laws/

judgments/

medical_templates/

assessment_guidelines/

hospital SOPs/

These become our Compliance Knowledge Base.

====================================================

GOAL

Hospitals manually review medical documents before audits.

This takes hours.

Our AI automates

Document Understanding

Compliance Checking

Risk Detection

Audit Report Generation

Medical Chronology

Decision Support

====================================================

THIS IS NOT A CHATBOT

The AI should autonomously complete a workflow.

====================================================

CREATE AN MVP ONLY

====================================================

AGENT 1

Intake Agent

Responsibilities

Read uploaded PDFs

Extract

Patient Name

Doctor

Hospital

Diagnosis

Treatment

Medicines

Consent

Signatures

Dates

Return structured JSON

====================================================

AGENT 2

Compliance Intelligence Agent

Uses RAG.

Reads

Medical Rules

Hospital SOP

Guidelines

Templates

Checks

Missing Consent

Missing Signature

Missing Sections

Missing Diagnosis

Required Documentation

Policy Violations

Outputs

Compliance Score

Violations

Reasoning

Recommendations

====================================================

AGENT 3

Risk Assessment Agent

Input

Compliance Result

Output

High Risk

Medium Risk

Low Risk

Explain WHY.

Generate Risk Summary.

====================================================

AGENT 4

Audit Report Agent

Generate

Medical Chronology

Compliance Report

Audit Summary

Executive Summary

Recommendations

Export PDF

====================================================

LANGCHAIN

Use LangChain for

PDF Loading

Chunking

Embeddings

Retriever

Prompt Templates

Tool Calling

ChromaDB

RAG

LLM

====================================================

LANGGRAPH

Use LangGraph as the workflow orchestrator.

Workflow

Upload

↓

Intake Agent

↓

Compliance Agent

↓

Risk Agent

↓

Audit Agent

↓

Finish

====================================================

MVP UI

Reuse existing UI.

Only add

Compliance Dashboard

Compliance Score Card

Risk Card

Violations Table

Audit Report Button

Medical Chronology Button

====================================================

TECH STACK

React

FastAPI

LangGraph

LangChain

Gemini

ChromaDB

PyMuPDF

PostgreSQL (reuse existing if available)

Tailwind

====================================================

DELIVERABLES

Create

PLAN.md

README.md

Architecture.md

Folder Structure

LangGraph Workflow

Working MVP

====================================================

PHASE 1

Reuse Existing Project

Create new folder

Rename project

Reuse backend

Reuse frontend

Reuse RAG

Reuse uploader

Reuse parser

Reuse embeddings

Reuse vector database

Reuse prompts

Reuse templates

Reuse dashboard

====================================================

PHASE 2

Implement LangGraph

Create Intake Agent

Create Compliance Agent

Create Risk Agent

Create Audit Agent

Connect agents

Connect RAG

Connect existing knowledge base

====================================================

PHASE 3

Create Compliance Dashboard

Generate Compliance Score

Generate Risk Analysis

Generate Audit Report

Generate Medical Chronology

Export Reports

Test End-to-End

====================================================

IMPORTANT

Every AI agent must have

Goal

Input

Output

Prompt

Tools Used

LLM

Failure Handling

====================================================

The code should be modular.

Reuse as much existing code as possible.

Avoid duplicate files.

Avoid unnecessary rewrites.

Keep the system hackathon-ready.

Generate a complete MVP that can be demonstrated in 5 minutes and aligns with AgentCon 2026 judging criteria.
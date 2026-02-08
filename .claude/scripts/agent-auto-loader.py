#!/usr/bin/env python3
"""
Agent Auto-Loader for Claude Code
Automatically loads all agent capabilities into Claude's context on session start
"""

import os
import json
import sys
from pathlib import Path

def load_all_agents(agents_dir):
    """Load all agent markdown files and extract their capabilities"""
    
    agents_dir = Path(agents_dir)
    if not agents_dir.exists():
        return {"error": "Agents directory not found"}
    
    agents_summary = {
        "total_agents": 0,
        "agents_by_category": {},
        "agent_capabilities": []
    }
    
    # Categories mapping
    categories = {
        "frontend": ["react", "frontend", "nextjs", "ui", "ux", "component"],
        "backend": ["backend", "api", "server", "database", "graphql"],
        "devops": ["devops", "deployment", "cloud", "docker", "kubernetes", "infrastructure"],
        "testing": ["test", "qa", "debug", "playwright", "security", "audit"],
        "research": ["research", "analyst", "data", "market", "competitive"],
        "ai_ml": ["ai", "ml", "model", "prompt", "mcp"],
        "content": ["content", "marketing", "seo", "social", "writer"],
        "design": ["design", "3d", "video", "diagram", "visual"],
        "business": ["business", "product", "sales", "legal", "compliance"],
        "web3": ["web3", "blockchain", "smart-contract", "solidity"],
        "performance": ["performance", "optimization", "profiler"],
        "documentation": ["documentation", "technical-writer", "changelog"]
    }
    
    for agent_file in agents_dir.glob("*.md"):
        agents_summary["total_agents"] += 1
        agent_name = agent_file.stem
        
        # Read first 500 chars to get description
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read(1000)
                
                # Extract name from frontmatter if exists
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        if 'name:' in frontmatter:
                            for line in frontmatter.split('\n'):
                                if line.strip().startswith('name:'):
                                    agent_name = line.split(':', 1)[1].strip().strip('"').strip("'")
                                    break
                        if 'description:' in frontmatter:
                            for line in frontmatter.split('\n'):
                                if line.strip().startswith('description:'):
                                    description = line.split(':', 1)[1].strip().strip('"').strip("'")
                                    break
                        else:
                            description = f"Specialized agent: {agent_name}"
                    else:
                        description = f"Agent: {agent_name}"
                else:
                    # Extract first heading or paragraph
                    lines = content.split('\n')
                    description = next((line.strip('# ').strip() for line in lines if line.strip()), agent_name)
        except Exception as e:
            description = f"Agent: {agent_name}"
        
        # Categorize agent
        agent_lower = agent_file.stem.lower()
        assigned_category = "general"
        
        for category, keywords in categories.items():
            if any(keyword in agent_lower for keyword in keywords):
                assigned_category = category
                break
        
        if assigned_category not in agents_summary["agents_by_category"]:
            agents_summary["agents_by_category"][assigned_category] = []
        
        agents_summary["agents_by_category"][assigned_category].append({
            "file": agent_file.stem,
            "name": agent_name,
            "description": description[:200]  # Limit description length
        })
        
        agents_summary["agent_capabilities"].append({
            "file": agent_file.stem,
            "name": agent_name,
            "category": assigned_category
        })
    
    return agents_summary

def generate_context_output(agents_summary):
    """Generate formatted output for Claude's context"""
    
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"""
# Available Specialized Agents

You have access to {agents_summary['total_agents']} specialized agents organized by domain:

## Agent Categories and Capabilities

"""
        }
    }
    
    # Add categories
    for category, agents in sorted(agents_summary["agents_by_category"].items()):
        category_name = category.replace("_", " ").title()
        output["hookSpecificOutput"]["additionalContext"] += f"\n### {category_name} ({len(agents)} agents)\n"
        
        for agent in sorted(agents, key=lambda x: x['file']):
            output["hookSpecificOutput"]["additionalContext"] += f"- **@{agent['file']}**: {agent['description']}\n"
    
    output["hookSpecificOutput"]["additionalContext"] += """

## How to Use Agents

When a user request relates to any of these domains, YOU SHOULD AUTOMATICALLY invoke the relevant agent(s) using @agent-name syntax.

Examples:
- Frontend task → Invoke @expert-react-frontend-engineer or @frontend-developer
- Backend task → Invoke @backend-architect or @api-documenter  
- Research task → Invoke @research-orchestrator or @comprehensive-researcher
- Security task → Invoke @security-auditor or @penetration-tester

YOU MUST be proactive in selecting and invoking appropriate agents based on the user's needs. Do not wait for the user to specify which agent to use.
"""
    
    return output

if __name__ == "__main__":
    # Get agents directory from environment or use default
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    agents_dir = os.path.join(project_dir, '.claude', 'agents')
    
    # Load agents
    agents_summary = load_all_agents(agents_dir)
    
    if "error" in agents_summary:
        print(json.dumps({"error": agents_summary["error"]}))
        sys.exit(0)
    
    # Generate and output context
    output = generate_context_output(agents_summary)
    print(json.dumps(output))
    sys.exit(0)

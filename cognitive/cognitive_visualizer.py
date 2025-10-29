"""
Cognitive Process Visualization System

This module provides visualization capabilities for cognitive code generation processes,
enabling researchers to analyze and understand the cognitive workflow.
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import seaborn as sns
from datetime import datetime
import pandas as pd
import numpy as np


class CognitiveVisualizer:
    """
    Visualizes cognitive processes during code generation

    Provides multiple visualization types for analyzing cognitive workflow,
    decision-making processes, and cognitive load patterns.
    """

    def __init__(self, style: str = "seaborn-v0_8"):
        """Initialize visualizer with specified style"""
        try:
            plt.style.use(style)
        except:
            plt.style.use("default")

        self.colors = {
            "problem_comprehension": "#FF6B6B",
            "solution_planning": "#4ECDC4",
            "algorithm_design": "#45B7D1",
            "implementation": "#96CEB4",
            "validation": "#FFEAA7",
            "optimization": "#DDA0DD",
            "reflection": "#98D8C8"
        }

    def visualize_cognitive_workflow(self, analysis_data: Dict[str, Any], output_path: Optional[str] = None):
        """
        Create comprehensive visualization of cognitive workflow

        Args:
            analysis_data: Cognitive analysis data from generation session
            output_path: Path to save visualization (optional)
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Cognitive Code Generation Analysis", fontsize=16, fontweight='bold')

        # 1. Cognitive Stages Timeline
        self._plot_cognitive_stages(analysis_data, axes[0, 0])

        # 2. Cognitive Load Breakdown
        self._plot_cognitive_load(analysis_data, axes[0, 1])

        # 3. Reasoning Chain Flow
        self._plot_reasoning_chain(analysis_data, axes[1, 0])

        # 4. Strategy and Confidence Metrics
        self._plot_metrics(analysis_data, axes[1, 1])

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"📊 Visualization saved to: {output_path}")
        else:
            plt.show()

        return fig

    def _plot_cognitive_stages(self, analysis_data: Dict[str, Any], ax):
        """Plot cognitive stages timeline"""
        stages = analysis_data.get("thinking_stages", [])

        if not stages:
            ax.text(0.5, 0.5, "No cognitive stages data", ha='center', va='center')
            ax.set_title("Cognitive Stages Timeline")
            return

        stage_names = [stage.get("stage", "unknown") for stage in stages]
        stage_colors = [self.colors.get(stage, "#cccccc") for stage in stage_names]

        y_pos = np.arange(len(stage_names))

        # Create horizontal bar chart
        bars = ax.barh(y_pos, [1] * len(stage_names), color=stage_colors, alpha=0.7)

        ax.set_yticks(y_pos)
        ax.set_yticklabels([stage.replace("_", " ").title() for stage in stage_names])
        ax.set_xlabel("Cognitive Processing")
        ax.set_title("Cognitive Stages Timeline")
        ax.set_xlim(0, 1.2)

        # Add stage focus as text
        for i, stage in enumerate(stages):
            focus = stage.get("focus", "")[:30] + "..." if len(stage.get("focus", "")) > 30 else stage.get("focus", "")
            ax.text(1.1, i, focus, va='center', fontsize=8)

    def _plot_cognitive_load(self, analysis_data: Dict[str, Any], ax):
        """Plot cognitive load breakdown"""
        load_data = analysis_data.get("cognitive_load", {})

        if not load_data:
            ax.text(0.5, 0.5, "No cognitive load data", ha='center', va='center')
            ax.set_title("Cognitive Load Analysis")
            return

        loads = [
            load_data.get("intrinsic_load", 0),
            load_data.get("extraneous_load", 0),
            load_data.get("germane_load", 0)
        ]
        labels = ["Intrinsic\n(Problem)", "Extraneous\n(Implementation)", "Germane\n(Learning)"]
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(loads, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90)

        ax.set_title("Cognitive Load Breakdown")

        # Add total load indicator
        total_load = load_data.get("total_load", sum(loads))
        ax.text(0, -1.3, f"Total Load: {total_load:.2f}", ha='center', fontweight='bold')

    def _plot_reasoning_chain(self, analysis_data: Dict[str, Any], ax):
        """Plot reasoning chain as a flow diagram"""
        reasoning_chain = analysis_data.get("reasoning_chain", [])

        if not reasoning_chain:
            ax.text(0.5, 0.5, "No reasoning chain data", ha='center', va='center')
            ax.set_title("Reasoning Chain Flow")
            return

        # Create simple flow chart
        y_positions = np.linspace(1, 0, len(reasoning_chain))

        for i, step in enumerate(reasoning_chain):
            # Truncate long text
            text = step[:40] + "..." if len(step) > 40 else step

            # Draw box
            box = plt.Rectangle((0.1, y_positions[i] - 0.03), 0.8, 0.06,
                              facecolor='lightblue', edgecolor='blue', alpha=0.7)
            ax.add_patch(box)

            # Add text
            ax.text(0.5, y_positions[i], f"{i+1}. {text}", ha='center', va='center',
                   fontsize=8, wrap=True)

            # Draw arrow to next step
            if i < len(reasoning_chain) - 1:
                ax.arrow(0.5, y_positions[i] - 0.05, 0, -0.05,
                        head_width=0.02, head_length=0.01, fc='blue', ec='blue')

        ax.set_xlim(0, 1)
        ax.set_ylim(-0.1, 1.1)
        ax.set_title("Reasoning Chain Flow")
        ax.axis('off')

    def _plot_metrics(self, analysis_data: Dict[str, Any], ax):
        """Plot strategy and confidence metrics"""
        confidence = analysis_data.get("confidence", 0)
        strategy = analysis_data.get("strategy_used", "unknown")

        # Create gauge-like visualization for confidence
        angles = np.linspace(0, np.pi, 100)
        confidence_angle = confidence * np.pi

        # Draw semicircle gauge
        x = np.cos(angles)
        y = np.sin(angles)
        ax.plot(x, y, 'k-', linewidth=2)

        # Fill confidence area
        confidence_x = np.cos(np.linspace(0, confidence_angle, int(confidence * 100)))
        confidence_y = np.sin(np.linspace(0, confidence_angle, int(confidence * 100)))
        ax.fill_between(confidence_x, 0, confidence_y, alpha=0.7, color='green')

        # Add needle
        needle_angle = confidence_angle
        ax.plot([0, np.cos(needle_angle)], [0, np.sin(needle_angle)], 'r-', linewidth=3)

        # Add labels
        ax.text(0, -0.3, f"Confidence: {confidence:.1%}", ha='center', fontweight='bold')
        ax.text(0, -0.5, f"Strategy: {strategy.replace('_', ' ').title()}", ha='center')

        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title("Performance Metrics")

    def create_cognitive_network(self, analysis_data: Dict[str, Any], output_path: Optional[str] = None):
        """
        Create network visualization of cognitive relationships

        Args:
            analysis_data: Cognitive analysis data
            output_path: Path to save network diagram
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        # Create network graph
        G = nx.DiGraph()

        # Add cognitive stages as nodes
        stages = analysis_data.get("thinking_stages", [])
        for i, stage in enumerate(stages):
            stage_name = stage.get("stage", f"stage_{i}")
            G.add_node(stage_name,
                      type="cognitive_stage",
                      focus=stage.get("focus", ""))

        # Add edges between consecutive stages
        for i in range(len(stages) - 1):
            current_stage = stages[i].get("stage", f"stage_{i}")
            next_stage = stages[i+1].get("stage", f"stage_{i+1}")
            G.add_edge(current_stage, next_stage)

        # Add decision nodes
        decisions = analysis_data.get("cognitive_trace", {}).get("decisions", [])
        for i, decision in enumerate(decisions):
            decision_node = f"decision_{i}"
            G.add_node(decision_node,
                      type="decision",
                      reasoning=decision.get("reasoning", ""))

        # Layout and draw
        pos = nx.spring_layout(G, k=3, iterations=50)

        # Draw nodes with different colors based on type
        stage_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "cognitive_stage"]
        decision_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "decision"]

        nx.draw_networkx_nodes(G, pos, nodelist=stage_nodes,
                              node_color='lightblue', node_size=1500, alpha=0.7)
        nx.draw_networkx_nodes(G, pos, nodelist=decision_nodes,
                              node_color='lightcoral', node_size=1000, alpha=0.7)

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)

        # Draw labels
        labels = {node: node.replace("_", " ").title() for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        ax.set_title("Cognitive Process Network", fontsize=14, fontweight='bold')
        ax.axis('off')

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"🕸️ Network visualization saved to: {output_path}")
        else:
            plt.show()

        return fig

    def generate_cognitive_report(self, session_dir: str, output_name: str = "cognitive_report"):
        """
        Generate comprehensive cognitive analysis report with visualizations

        Args:
            session_dir: Directory containing cognitive analysis data
            output_name: Name for output files
        """
        session_path = Path(session_dir)
        analysis_file = session_path / "cognitive_analysis.json"

        if not analysis_file.exists():
            print(f"❌ Analysis file not found: {analysis_file}")
            return

        # Load analysis data
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)

        # Create visualizations
        workflow_viz_path = session_path / f"{output_name}_workflow.png"
        network_viz_path = session_path / f"{output_name}_network.png"

        print("🎨 Generating cognitive visualizations...")

        # Generate workflow visualization
        self.visualize_cognitive_workflow(analysis_data, str(workflow_viz_path))

        # Generate network visualization
        self.create_cognitive_network(analysis_data, str(network_viz_path))

        print(f"✅ Cognitive report generated successfully!")
        print(f"📊 Workflow visualization: {workflow_viz_path}")
        print(f"🕸️ Network visualization: {network_viz_path}")

        return {
            "workflow_viz": str(workflow_viz_path),
            "network_viz": str(network_viz_path),
            "analysis_data": analysis_data
        }


def demonstrate_visualization():
    """Demonstrate the cognitive visualization system"""
    # Sample analysis data for demonstration
    sample_data = {
        "thinking_stages": [
            {"stage": "problem_comprehension", "focus": "Understanding the requirement"},
            {"stage": "solution_planning", "focus": "Planning the approach"},
            {"stage": "algorithm_design", "focus": "Designing the algorithm"},
            {"stage": "implementation", "focus": "Writing the code"},
            {"stage": "validation", "focus": "Testing the solution"},
            {"stage": "reflection", "focus": "Evaluating the result"}
        ],
        "cognitive_load": {
            "intrinsic_load": 0.6,
            "extraneous_load": 0.3,
            "germane_load": 0.4,
            "total_load": 1.3
        },
        "reasoning_chain": [
            "Stage: problem_comprehension - Understanding the requirement",
            "Stage: solution_planning - Planning the approach",
            "Decision: Selected top-down strategy based on problem complexity",
            "Stage: algorithm_design - Designing the algorithm",
            "Stage: implementation - Writing the code"
        ],
        "confidence": 0.85,
        "strategy_used": "top_down",
        "cognitive_trace": {
            "decisions": [
                {"reasoning": "Selected top-down strategy based on problem complexity"},
                {"reasoning": "Chose iterative approach for better readability"}
            ]
        }
    }

    visualizer = CognitiveVisualizer()

    print("🎨 Demonstrating cognitive visualization...")
    visualizer.visualize_cognitive_workflow(sample_data)
    visualizer.create_cognitive_network(sample_data)


if __name__ == "__main__":
    demonstrate_visualization()
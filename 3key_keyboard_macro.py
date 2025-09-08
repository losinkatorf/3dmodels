#!/usr/bin/env python3
"""
FreeCAD Macro: 3-Key Keyboard
Creates a parametric 3-key keyboard using Part Design workbench
Features: Base, buttons, cable hole, and microswitch sockets

Author: Created for 3D Models Repository
Date: September 2025
"""

import FreeCAD as App
import FreeCADGui as Gui
import Part
import PartDesign
import Sketcher

def create_3key_keyboard():
    """Main function to create the 3-key keyboard model"""
    
    # Create new document
    doc = App.newDocument('3KeyKeyboard')
    
    # Parameters (easily modifiable)
    params = {
        # Base dimensions
        'base_length': 120.0,
        'base_width': 40.0, 
        'base_height': 15.0,
        'base_fillet': 3.0,
        
        # Button parameters
        'button_diameter': 12.0,
        'button_height': 8.0,
        'button_spacing': 35.0,
        'button_offset_y': 0.0,  # Center buttons
        
        # Microswitch socket parameters
        'socket_width': 6.0,
        'socket_length': 6.0,
        'socket_depth': 10.0,
        'socket_offset_z': 2.0,  # From bottom
        
        # Cable hole parameters
        'cable_diameter': 6.0,
        'cable_hole_x': -50.0,  # Position from center
        'cable_hole_z': 7.5,    # Height from bottom
        
        # Wall thickness
        'wall_thickness': 2.0
    }
    
    # Create Part Design Body for the main keyboard
    body = doc.addObject('PartDesign::Body', 'KeyboardBody')
    
    # === CREATE BASE SKETCH ===
    base_sketch = body.newObject('Sketcher::SketchObject', 'BaseSketch')
    base_sketch.Support = (doc.getObject('XY_Plane'),)
    base_sketch.MapMode = 'FlatFace'
    
    # Create base rectangle
    base_sketch.addGeometry(Part.LineSegment(
        App.Vector(-params['base_length']/2, -params['base_width']/2, 0),
        App.Vector(params['base_length']/2, -params['base_width']/2, 0)
    ), False)
    base_sketch.addGeometry(Part.LineSegment(
        App.Vector(params['base_length']/2, -params['base_width']/2, 0),
        App.Vector(params['base_length']/2, params['base_width']/2, 0)
    ), False)
    base_sketch.addGeometry(Part.LineSegment(
        App.Vector(params['base_length']/2, params['base_width']/2, 0),
        App.Vector(-params['base_length']/2, params['base_width']/2, 0)
    ), False)
    base_sketch.addGeometry(Part.LineSegment(
        App.Vector(-params['base_length']/2, params['base_width']/2, 0),
        App.Vector(-params['base_length']/2, -params['base_width']/2, 0)
    ), False)
    
    # Add constraints for base rectangle
    for i in range(4):
        base_sketch.addConstraint(Sketcher.Constraint('Coincident', i, 2, (i+1)%4, 1))
    
    # Add dimensional constraints
    base_sketch.addConstraint(Sketcher.Constraint('Horizontal', 0))
    base_sketch.addConstraint(Sketcher.Constraint('Vertical', 1))
    base_sketch.addConstraint(Sketcher.Constraint('DistanceX', 0, params['base_length']))
    base_sketch.addConstraint(Sketcher.Constraint('DistanceY', 1, params['base_width']))
    
    doc.recompute()
    
    # === CREATE BASE PAD ===
    base_pad = body.newObject('PartDesign::Pad', 'BasePad')
    base_pad.Profile = base_sketch
    base_pad.Length = params['base_height']
    base_pad.Type = 0  # Length
    doc.recompute()
    
    # === ADD BASE FILLETS ===
    base_fillet = body.newObject('PartDesign::Fillet', 'BaseFillet')
    base_fillet.Base = base_pad
    # Get all vertical edges for filleting
    edges = []
    for i, edge in enumerate(base_pad.Shape.Edges):
        if abs(edge.tangentAt(edge.FirstParameter).z) < 0.1:  # Vertical edges
            edges.append((base_pad, [f'Edge{i+1}']))
    base_fillet.Edges = edges
    base_fillet.Radius = params['base_fillet']
    doc.recompute()
    
    # === CREATE BUTTON HOLES ===
    # Sketch for button holes
    button_sketch = body.newObject('Sketcher::SketchObject', 'ButtonHolesSketch')
    button_sketch.Support = (base_fillet, ['Face1'])  # Top face
    button_sketch.MapMode = 'FlatFace'
    
    # Create three button holes
    for i in range(3):
        x_pos = (i - 1) * params['button_spacing']  # -1, 0, 1 positions
        y_pos = params['button_offset_y']
        
        # Add circle for button hole
        button_sketch.addGeometry(Part.Circle(
            App.Vector(x_pos, y_pos, 0), 
            App.Vector(0, 0, 1), 
            params['button_diameter']/2
        ), False)
        
        # Add radius constraint
        button_sketch.addConstraint(Sketcher.Constraint('Radius', i, params['button_diameter']/2))
        
        # Position constraints
        if i == 1:  # Center button
            button_sketch.addConstraint(Sketcher.Constraint('PointOnObject', i, 3, -1))  # Center on origin
        else:
            # Distance from center button
            button_sketch.addConstraint(Sketcher.Constraint('Distance', 1, 3, i, 3, params['button_spacing']))
    
    doc.recompute()
    
    # Create pocket for button holes
    button_pocket = body.newObject('PartDesign::Pocket', 'ButtonHolesPocket')
    button_pocket.Profile = button_sketch
    button_pocket.Type = 1  # Through all
    doc.recompute()
    
    # === CREATE MICROSWITCH SOCKETS ===
    # Sketch for microswitch sockets
    socket_sketch = body.newObject('Sketcher::SketchObject', 'SocketSketch')
    socket_sketch.Support = (base_fillet, ['Face2'])  # Bottom face
    socket_sketch.MapMode = 'FlatFace'
    
    # Create socket rectangles under each button
    for i in range(3):
        x_pos = (i - 1) * params['button_spacing']
        y_pos = params['button_offset_y']
        
        # Create rectangle for socket
        socket_sketch.addGeometry(Part.LineSegment(
            App.Vector(x_pos - params['socket_length']/2, y_pos - params['socket_width']/2, 0),
            App.Vector(x_pos + params['socket_length']/2, y_pos - params['socket_width']/2, 0)
        ), False)
        socket_sketch.addGeometry(Part.LineSegment(
            App.Vector(x_pos + params['socket_length']/2, y_pos - params['socket_width']/2, 0),
            App.Vector(x_pos + params['socket_length']/2, y_pos + params['socket_width']/2, 0)
        ), False)
        socket_sketch.addGeometry(Part.LineSegment(
            App.Vector(x_pos + params['socket_length']/2, y_pos + params['socket_width']/2, 0),
            App.Vector(x_pos - params['socket_length']/2, y_pos + params['socket_width']/2, 0)
        ), False)
        socket_sketch.addGeometry(Part.LineSegment(
            App.Vector(x_pos - params['socket_length']/2, y_pos + params['socket_width']/2, 0),
            App.Vector(x_pos - params['socket_length']/2, y_pos - params['socket_width']/2, 0)
        ), False)
        
        # Add constraints
        base_idx = i * 4
        for j in range(4):
            socket_sketch.addConstraint(Sketcher.Constraint('Coincident', base_idx + j, 2, base_idx + (j+1)%4, 1))
        
        # Dimensional constraints
        socket_sketch.addConstraint(Sketcher.Constraint('DistanceX', base_idx, params['socket_length']))
        socket_sketch.addConstraint(Sketcher.Constraint('DistanceY', base_idx + 1, params['socket_width']))
    
    doc.recompute()
    
    # Create pocket for sockets
    socket_pocket = body.newObject('PartDesign::Pocket', 'SocketPocket')
    socket_pocket.Profile = socket_sketch
    socket_pocket.Length = params['socket_depth']
    socket_pocket.Type = 0  # Length
    doc.recompute()
    
    # === CREATE CABLE HOLE ===
    # Sketch for cable hole
    cable_sketch = body.newObject('Sketcher::SketchObject', 'CableHoleSketch')
    cable_sketch.Support = (doc.getObject('YZ_Plane'),)
    cable_sketch.MapMode = 'FlatFace'
    
    # Create circle for cable hole
    cable_sketch.addGeometry(Part.Circle(
        App.Vector(0, params['cable_hole_z'], 0),
        App.Vector(1, 0, 0),
        params['cable_diameter']/2
    ), False)
    
    # Add constraints
    cable_sketch.addConstraint(Sketcher.Constraint('Radius', 0, params['cable_diameter']/2))
    cable_sketch.addConstraint(Sketcher.Constraint('DistanceY', 0, 3, -2, params['cable_hole_z']))
    
    doc.recompute()
    
    # Create pocket for cable hole
    cable_pocket = body.newObject('PartDesign::Pocket', 'CableHolePocket')
    cable_pocket.Profile = cable_sketch
    cable_pocket.Type = 1  # Through all
    doc.recompute()
    
    # === CREATE BUTTONS ===
    # Create separate body for buttons
    button_body = doc.addObject('PartDesign::Body', 'ButtonsBody')
    
    # Button sketch
    button_sketch_obj = button_body.newObject('Sketcher::SketchObject', 'ButtonSketch')
    button_sketch_obj.Support = (doc.getObject('XY_Plane'),)
    button_sketch_obj.MapMode = 'FlatFace'
    
    # Create one button (will be mirrored/patterned)
    button_sketch_obj.addGeometry(Part.Circle(
        App.Vector(0, 0, 0),
        App.Vector(0, 0, 1),
        (params['button_diameter'] - 1)/2  # Slightly smaller than hole
    ), False)
    
    button_sketch_obj.addConstraint(Sketcher.Constraint('Radius', 0, (params['button_diameter'] - 1)/2))
    button_sketch_obj.addConstraint(Sketcher.Constraint('Coincident', 0, 3, -1))
    
    doc.recompute()
    
    # Create button pad
    button_pad = button_body.newObject('PartDesign::Pad', 'ButtonPad')
    button_pad.Profile = button_sketch_obj
    button_pad.Length = params['button_height']
    button_pad.Type = 0
    doc.recompute()
    
    # Create linear pattern for 3 buttons
    button_pattern = button_body.newObject('PartDesign::LinearPattern', 'ButtonPattern')
    button_pattern.Originals = [button_pad]
    button_pattern.Direction = (doc.getObject('X_Axis'), [''])
    button_pattern.Length = 2 * params['button_spacing']
    button_pattern.Occurrences = 3
    doc.recompute()
    
    # Position buttons above the base
    button_body.Placement = App.Placement(
        App.Vector(0, 0, params['base_height']),
        App.Rotation(0, 0, 0, 1)
    )
    
    # === FINAL SETUP ===
    # Set view to isometric
    Gui.activeDocument().activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
    
    # Set colors
    body.ViewObject.ShapeColor = (0.8, 0.8, 0.9)  # Light blue-gray for base
    button_body.ViewObject.ShapeColor = (0.2, 0.2, 0.2)  # Dark gray for buttons
    
    doc.recompute()
    
    print("3-Key Keyboard model created successfully!")
    print("\nModel Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    print(f"\nTo modify the design:")
    print(f"1. Edit sketches to change dimensions")
    print(f"2. Modify pad/pocket lengths")
    print(f"3. Adjust fillet radii")
    print(f"4. Change button spacing in the linear pattern")
    
    return doc

# Execute the macro
if __name__ == '__main__':
    create_3key_keyboard()

#version 130

out vec4 color;
out vec2 tex_coord;

void main() {
    gl_Position = ftransform();
    color = gl_Color;
    tex_coord = gl_MultiTexCoord0.xy;
}
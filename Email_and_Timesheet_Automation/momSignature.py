import os
import json


def generate_signature():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "../settings.json")

    try:
        # Open and read the JSON file
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        role = config.get("role", "")
        first_line_role = role.splitlines()[0]
        last_line_role = role.splitlines()[len(role.splitlines()) - 1]
        name = config.get("name", "")
        mobile_no = config.get("mobile_no", "")
        email = config.get("email", "")

    except FileNotFoundError:
        print("Error: settings.json file not found.")



    html_content = f"""
    <table id="logo" style="text-align: left; background-color: white; width: 506.7pt; color: rgb(66, 66, 66); box-sizing: border-box; border-collapse: collapse; border-spacing: 0px;">
<tbody>
<tr>
<td style="text-align: left; padding-right: 10.5pt; padding-left: 0.75pt; vertical-align: top; width: 129.75pt; height: 91.75pt;">
<p align="center" style="margin-top: 0px; margin-bottom: 0px;"><span style="font-family: Arial, sans-serif; font-size: 12pt; color: black;"><a href="http://www.xalta.tech/" target="_blank" title="&quot;www.xalta.tech&quot; t" rel="noopener noreferrer" data-auth="NotApplicable" data-linkindex="2" style="margin: 0px;" id="OWAf988faf1-a8c3-66e1-d721-7b2f24a4bce8" class="OWAAutoLink"><img src="https://github.com/Anand-kale/UiPathDocumentation/blob/368e3d6275fe21a677a1d3da2b0b863dd2566c38/f2fde266-b69f-4d6c-b24a-5f802de58b97.png?raw=true" id="x_x_Picture_x0020_3" data-outlook-trace="F:1|T:1" width="160" height="81" style="width: 160px; height: 81px; min-width: auto; min-height: auto; margin: 0px; vertical-align: top;" loadstarttime="1732016046754"></a>&nbsp;</span></p>
</td>
<td style="text-align: left; border-left: 1pt solid rgb(189, 189, 189); padding-left: 10.5pt; vertical-align: top; width: 376.8pt; height: 91.75pt;">
<table style="text-align: left; box-sizing: border-box; border-collapse: collapse; border-spacing: 0px;">
<tbody>
<tr>
<td style="text-align: left; padding: 0.75pt; width: 472.333px; height: 66px;">
<p style="text-align: left; margin-top: 0px; margin-bottom: 0px;"><span style="font-family: &quot;Segoe UI&quot;, sans-serif; font-size: 15px; color: rgb(100, 100, 100);"><b>{name}<br></b></span><span style="font-family: &quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif; font-size: 15px; color: rgb(66, 66, 66);">{first_line_role}</span></p>
<p
style="text-align: left; margin-top: 0px; margin-bottom: 0px;"><span style="font-family: &quot;Segoe UI&quot;, &quot;Segoe UI Web (West European)&quot;, &quot;Segoe UI&quot;, -apple-system, BlinkMacSystemFont, Roboto, &quot;Helvetica Neue&quot;, sans-serif; font-size: 15px; color: rgb(66, 66, 66);">{last_line_role}</span></p>
</td>
</tr>
<tr>
<td style="text-align: left; padding: 0.75pt; width: 472.333px; height: 97px;">
<table style="text-align: left; box-sizing: border-box; border-collapse: collapse; border-spacing: 0px;">
<tbody>
<tr>
<td style="text-align: left; padding: 0.75pt 0; width: 357.75pt; height: 36.3333px;">
<p style="text-align: left; margin: 0px 0.1pt;"><span style="font-family: &quot;Segoe UI&quot;, sans-serif; font-size: 10pt; color: rgb(33, 33, 33);">M: {mobile_no}</span></p>
</td>
</tr>
<tr>
<td style="text-align: left;padding: 0.75pt 0; width: 188.25pt; height: 29.3333px;">
<p style="text-align: left; margin: 0px 0.1pt;"><span style="font-family: &quot;Segoe UI&quot;, sans-serif; font-size: 10pt; color: rgb(33, 33, 33);">E: {email}</span></p>
</td>
</tr>
<tr>
<td style="text-align: left;padding: 0.75pt 0; width: 188.25pt; height: 29.3333px;">
<p style="text-align: left; margin: 0px 0.1pt;"><span style="font-family: &quot;Segoe UI&quot;, sans-serif; font-size: 10pt; color: rgb(66, 66, 66);">www.xalta.tech</span></p>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>

"""

    return html_content


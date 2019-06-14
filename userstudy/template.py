INS_PREF_TEMPL = """
<h2>Which of two music clips do you prefer?</h2>

<p><b>Please use headphones in a quiet environment if possible.</b></p>
<p>You will be presented {batch_size} pairs of clips from video game music and asked which of the two clips you <i>prefer</i>.</p>
<p>In determining which clip you prefer, please make an reflex-based, intuitive decision based on your personal musical tastes and subjective reactions to hearing each song.</p>
<p><b>Feel free to listen to each song as many times as you like to make the decision.</b></p>
<p style="color:red;"><b>Please listen carefully! Your payment will depend on it.</b></p>
"""

INS_TURI_TEMPL = """
<h2>Which of two music clips do you think was composed by a human?</h2>

<p><b>Please use headphones in a quiet environment if possible.</b></p>
<p>You will be presented {batch_size} pairs of clips from video game music. Within each pair, one clip is composed by a human and the other is composed by a machine. You will be asked which of the two clips you think was <i>composed by a human</i>.</p>
<p>In determining which clip was composed by a human, please make a reflex-based decision based on your intuition. If you can't tell, choose your best guess.</p>
<p><b>Feel free to listen to each song as many times as you like to make the decision.</b></p>
<p style="color:red;"><b>Payment will depend upon your performance.</b></p>
"""

TEMPL = """

<style>
th, td {{
    border: 1px solid black;
    padding: 2px;
}}

th {{
    width: 100px;
    vertical-align: text-top;
    font-weight: normal;
}}

.noborder {{
    border: 0px solid black;
}}

td {{
    text-align: center;
    vertical-align: middle;
}}

tr.comp input[type=radio] {{
    border: 0px;
    width: 100%;
    height: 4em;
}}

audio {{
    width: 100%;
}}

input[type=submit] {{
    margin-top: 20px;
    width: 20em;
    height: 2em;
}}

div.experience input[type=radio] {{
    display: inline;
}}

#chiptunestudy {{
    max-width: 800px;
}}

.tclip {{
    width: 280px;
}}

.tpref {{
    width: 80px;
}}

</style>

<div id="chiptunestudy">

{instructions}

<div class="form-group">

<table>
<tbody>

{batch_items}

</tbody>
</table>

<div class="experience" id="musical_experience">
  <h3>Which statement most accurately reflects your <b><i>formal musical training</i> (e.g. learning to play an instrument)</b>?</h3>
  <input id="m1" class="form-control" type="radio" required="" name="musical_expertise" value="1"><label for="m1">I have no formal musical training.</label><br/>
  <input id="m2" class="form-control" type="radio" required="" name="musical_expertise" value="2"><label for="m2">I have some formal musical training (less than 5 years).</label><br/>
  <input id="m3" class="form-control" type="radio" required="" name="musical_expertise" value="3"><label for="m3">I have substantial formal musical training (more than 5 years).</label><br/>
</div>

<div class="experience" id="chiptune_experience">
  <h3>Which statement most accurately reflects your <b>listening experience with <i>chiptunes</i> (music from early video games)</b>?</h3>
  <input id="c1" class="form-control" type="radio" required="" name="chiptune_expertise" value="1"><label for="c1">I have never before listened to chiptunes.</label><br/>
  <input id="c2" class="form-control" type="radio" required="" name="chiptune_expertise" value="2"><label for="c2">I have listened to chiptunes while playing video games.</label><br/>
  <input id="c3" class="form-control" type="radio" required="" name="chiptune_expertise" value="3"><label for="c3">I have listened to chiptunes for pleasure outside of playing video games.</label><br/>
</div>

<input type="submit">

</div>

</div>
"""

ITEM_PREF_TEMPL = """
<tr class="comp_labels">
  <th class="tclip">Clip <b>A</b></th>
  <th class="tclip">Clip <b>B</b></th>
  <th class="tpref">Clip <b>A</b> preferred</th>
  <th class="tpref">Clip <b>B</b> preferred</th>
</tr>
<tr class="comp">
  <td class="tclip"><audio controls=""><source src="${{pair_{i}_clip_a_url}}" type="audio/mpeg"/></audio></td>
  <td class="tclip"><audio controls=""><source src="${{pair_{i}_clip_b_url}}" type="audio/mpeg"/></audio></td>
  <td class="tpref"><input class="form-control" type="radio" required="" name="pair_{i}_pref" value="A"></td>
  <td class="tpref"><input class="form-control" type="radio" required="" name="pair_{i}_pref" value="B"></td>
</tr>
"""

ITEM_TURI_TEMPL = """
<tr class="comp_labels">
  <th class="tclip">Clip <b>A</b></th>
  <th class="tclip">Clip <b>B</b></th>
  <th class="tpref">Clip <b>A</b> composed by human</th>
  <th class="tpref">Clip <b>B</b> composed by human</th>
</tr>
<tr class="comp">
  <td class="tclip"><audio controls=""><source src="${{pair_{i}_clip_a_url}}" type="audio/mpeg"/></audio></td>
  <td class="tclip"><audio controls=""><source src="${{pair_{i}_clip_b_url}}" type="audio/mpeg"/></audio></td>
  <td class="tpref"><input class="form-control" type="radio" required="" name="pair_{i}_pref" value="A"></td>
  <td class="tpref"><input class="form-control" type="radio" required="" name="pair_{i}_pref" value="B"></td>
</tr>
"""


import sys

n = int(sys.argv[1])

if 'turing' in sys.argv:
  instructions = INS_TURI_TEMPL.format(batch_size=n)
else:
  instructions = INS_PREF_TEMPL.format(batch_size=n)

batch_items = []
for i in range(n):
  if 'turing' in sys.argv:
    batch_items.append(ITEM_TURI_TEMPL.format(i=i))
  else:
    batch_items.append(ITEM_PREF_TEMPL.format(i=i))

print(TEMPL.format(instructions=instructions, batch_items='\n'.join(batch_items)))

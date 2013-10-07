<?php
    $f = implode('', file('../src/opcodes/z80gb.json'));
    $f = json_decode($f, true);

    function generate_opcodes() {
        $template = implode('', file('./opcodes.tmpl'));

        function table_header() {
            $s  = "<thead>\n";
            $s .= "<tr>\n";
            $s .= "<td></td>\n";
            for ($i = 0; $i < 16; $i++) {
                $s .= "<td>0x-" . dechex($i) . "</td>\n";
            }
            $s .= "</thead>\n";
            return $s;
        }
        function table_body() {
            global $f;
            $s  = "<tbody>\n";
            for ($i = 0; $i < 16; $i++) {
                $s .= "<tr>\n";
                $s .= "<td>0x" . dechex($i) . "-</td>\n";
                for ($j = 0; $j < 16; $j++) {
                    $x = dechex($i * 16 + $j);
                    if (strlen($x) == 1) $x = '0' . $x;
                    $s .= "<td>";
                    $s .= "0x" . $x;
                    $s .= "<br/>";
                    if (array_key_exists(strtoupper($x), $f)) {
                        $s .= "<a href=\"0x" . $x . "\">";
                        $s .= $f[strtoupper($x)]["op"];
                        $s .= ' ' . implode(",", $f[strtoupper($x)]["operands"]);
                        $s .= "</a>";
                    }
                    elseif (strtoupper($x) == 'CB') $s .= "<a href=\"opcodes_cb.html\">CB table</a>";
                    else $s .= "-";

                    $s .= "</td>\n";
                }
            }
            $s .= "</tbody>\n";
            return $s;
        }

        function table_footer() {
            return "<tfoot></tfoot>";
        }

        $s  = "<table id=\"opcodes-table\">\n";
        $s .= table_header();
        $s .= table_body();
        $s .= table_footer();
        $s .= "</table>";

        file_put_contents('./opcodes.html', str_replace('{{OPCODE-TABLE}}', $s, $template));
    }

    function generate_cb_opcodes() {
        $template = implode('', file('./opcodes_cb.tmpl'));

        function cb_table_header() {
            $s  = "<thead>\n";
            $s .= "<tr>\n";
            $s .= "<td></td>\n";
            for ($i = 0; $i < 16; $i++) {
                $s .= "<td>0xcb-" . dechex($i) . "</td>\n";
            }
            $s .= "</thead>\n";
            return $s;
        }
        function cb_table_body() {
            global $f;
            $s  = "<tbody>\n";
            for ($i = 0; $i < 16; $i++) {
                $s .= "<tr>\n";
                $s .= "<td>0xcb" . dechex($i) . "-</td>\n";
                for ($j = 0; $j < 16; $j++) {
                    $x = dechex($i * 16 + $j);
                    if (strlen($x) == 1) $x = '0' . $x;
                    $x = 'cb' . $x;
                    $s .= "<td>";
                    $s .= "0x" . $x;
                    $s .= "<br/>";
                    if (array_key_exists(strtoupper($x), $f)) {
                        $s .= "<a href=\"0x" . $x . "\">";
                        $s .= $f[strtoupper($x)]["op"];
                        $s .= ' ' . implode(",", $f[strtoupper($x)]["operands"]);
                        $s .= "</a>";
                    }
                    else $s .= "-";

                    $s .= "</td>\n";
                }
            }
            $s .= "</tbody>\n";
            return $s;
        }

        function cb_table_footer() {
            return "<tfoot></tfoot>";
        }

        $s  = "<table id=\"opcodes-table\">\n";
        $s .= cb_table_header();
        $s .= cb_table_body();
        $s .= cb_table_footer();
        $s .= "</table>";

        file_put_contents('./opcodes_cb.html', str_replace('{{OPCODE-TABLE}}', $s, $template));
    }

    generate_opcodes();
    generate_cb_opcodes();
?>